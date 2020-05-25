import os
import shutil
import json
import webbrowser
from zipfile import ZipFile
import sqlite3

from requests.exceptions import ConnectionError

from bridgestyle.sld import fromgeostyler
from .exporter import export_layer
from .serverbase import ServerBase
from .files import temp_filename_in_temp_folder
from .utils import is_vector, is_empty, is_postgis, layer_crs, layer_extent
from .apiconstants import VECTORFILE, RASTERFILE, POSTGIS


class GeoserverServer(ServerBase):

    FILE_BASED = 0
    POSTGIS_MANAGED_BY_BRIDGE = 1

    @staticmethod
    def servertype():
        return "geoserver"

    def __init__(
        self,
        name,
        url="",
        authid="",
        storage=0,
        db=None,
        use_original_data_source=False,
    ):
        super().__init__()
        self.name = name

        if url:
            if url.endswith("rest"):
                self.url = url.strip("/")
            else:
                self.url = url.strip("/") + "/rest"
        else:
            self.url = url

        self.authid = authid
        self.storage = storage
        self.db = db
        self.use_original_data_source = use_original_data_source
        self._workspace = ""

    def set_project_name(self, name):
        self._workspace = name

    def prepare_for_publishing(self, onlySymbology):        
        if not onlySymbology:
            self.delete_workspace()
        self._ensure_workspace_exists()
        self._uploaded_datasets = {}
        self._exported_layers = {}
        self._postgis_datastore_exists = False
        self._published_layers = set()

    def close_publishing(self):        
        pass

    def upload_resource(self, path, file):
        with open(file) as f:
            content = f.read()
        url = "%s/resource/%s" % (self.url, path)
        self.request(url, content, "put")

    def _save_style_as_zipped_sld(self, name, geostyler, icons, filename):
        sld, warnings = fromgeostyler.convert(geostyler)        
        z = ZipFile(filename, "w")
        for icon in icons.keys():
            if icon:
                z.write(icon, os.path.basename(icon))
        z.writestr(name + ".sld", sld)
        z.close()
        return warnings

    def publish_style(self, name, geostyler, icons):
        self._published_layers.add(name)
        style_filename = temp_filename_in_temp_folder(name + ".zip")
        warnings = self._save_style_as_zipped_sld(name, geostyler, icons, style_filename)
        for w in warnings:
            self.log_warning(w)
        self._publish_style(name, style_filename)
        return style_filename

    def publish_layer(self, name, sourcetype, source, fields=None):
        if sourcetype in [VECTORFILE, POSTGIS]:
            if is_empty(source):
                self.log_error("Layer contains zero features and cannot be published")
                return

            if sourcetype == POSTGIS and self.use_original_data_source:
                from .postgis import PostgisServer
                db = PostgisServer(
                    "temp",                    
                    source["host"],
                    source["port"],
                    source["schema"],
                    source["database"],
                )
                db.set_credentials(source["username"], source["password"])
                self._publish_vector_layer_from_postgis(name, db)
            elif self.storage in [self.FILE_BASED]:
                if source not in self._exported_layers:
                    path = export_layer(source, fields)
                    self._exported_layers[source] = path
                filename = self._exported_layers[source]
                self._publish_vector_layer_from_file(name, filename)
            elif self.storage == self.POSTGIS_MANAGED_BY_BRIDGE:
                from .servers import server_from_name
                db = server_from_name(self.db)
                if db is None:
                    raise Exception(
                        "GeocatBridge", "Cannot find the selected PostGIS database"                        
                    )
                db.import_layer(name, source, fields)
                self._publish_vector_layer_from_postgis(name, source, db)
        else:
            if source not in self._exported_layers:
                path = export_layer(source, fields)
                self._exported_layers[source] = path
            filename = self._exported_layers[source]
            self._publish_raster_layer(filename, name)

    def unpublish_data(self, name):
        self.delete_layer(name)
        self.delete_style(name)

    def base_url(self):
        return "/".join(self.url.split("/")[:-1])

    def _publish_vector_layer_from_file(self, name, filename):
        self.log_info("Publishing layer from file: %s" % filename)
        is_data_uploaded = filename in self._uploaded_datasets
        if not is_data_uploaded:
            with open(filename, "rb") as f:
                self._delete_datastore(name)
                url = "%s/workspaces/%s/datastores/%s/file.gpkg?update=overwrite" % (
                    self.url,
                    self._workspace,
                    name,
                )
                self.request(url, f.read(), "put")
            conn = sqlite3.connect(filename)
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM gpkg_geometry_columns")
            tablename = cursor.fetchall()[0][0]
            self._uploaded_datasets[filename] = (name, tablename)
        dataset_name, geoserver_layer_name = self._uploaded_datasets[filename]
        url = "%s/workspaces/%s/datastores/%s/featuretypes/%s.json" % (
            self.url,
            self._workspace,
            dataset_name,
            geoserver_layer_name,
        )
        r = self.request(url)
        ft = r.json()
        ft["featureType"]["name"] = name
        ft["featureType"]["title"] = name
        ext = layer_extent(filename)
        ft["featureType"]["nativeBoundingBox"] = {
            "minx": round(ext[0], 5),
            "maxx": round(ext[1], 5),
            "miny": round(ext[2], 5),
            "maxy": round(ext[3], 5),
            "srs": layer_crs(filename)
        }
        if is_data_uploaded:
            url = "%s/workspaces/%s/datastores/%s/featuretypes" % (
                self.url,
                self._workspace,
                datasetName,
            )
            r = self.request(url, ft, "post")
        else:
            r = self.request(url, ft, "put")
        self.log_info("Feature type correctly created from GPKG file '%s'" % filename)
        self._set_layer_style(name, name)

    def _publish_vector_layer_from_postgis(self, name, source, db):
        username, password = db.get_credentials()

        def _entry(k, v):
            return {"@key": k, "$": v}

        ds = {
            "dataStore": {
                "name": name,
                "type": "PostGIS",
                "enabled": True,
                "connectionParameters": {
                    "entry": [
                        _entry("schema", db.schema),
                        _entry("port", str(db.port)),
                        _entry("database", db.database),
                        _entry("passwd", password),
                        _entry("user", username),
                        _entry("host", db.host),
                        _entry("dbtype", "postgis"),
                    ]
                },
            }
        }
        dsUrl = "%s/workspaces/%s/datastores/" % (self.url, self._workspace)
        self.request(dsUrl, data=ds, method="post")
        ft = {"featureType": {"name": name, "srs": layer_crs(source)}}
        ftUrl = "%s/workspaces/%s/datastores/%s/featuretypes" % (
            self.url,
            self._workspace,
            name,
        )
        self.request(ftUrl, data=ft, method="post")
        self._set_layer_style(name, name)

    def _publish_raster_layer(self, filename, layername):
        # feedback.setText("Publishing data for layer %s" % layername)
        self._ensure_workspace_exists()
        with open(filename, "rb") as f:
            url = "%s/workspaces/%s/coveragestores/%s/file.geotiff" % (
                self.url,
                self._workspace,
                layername,
            )
            self.request(url, f.read(), "put")
        self.log_info("Feature type correctly created from Tiff file '%s'" % filename)
        self._set_layer_style(layername, layername)

    def create_groups(self, groups):
        for group in groups:
            self._publish_group(group)

    def _publish_group(self, group):
        layers = []
        for layer in group["layers"]:
            if isinstance(layer, dict):
                layers.append(
                    {
                        "@type": "layerGroup",
                        "name": "%s:%s" % (self._workspace, layer["name"]),
                    }
                )
                self._publish_group(layer)
            else:
                layers.append(
                    {"@type": "layer", "name": "%s:%s" % (self._workspace, layer)}
                )

        groupdef = {
            "layerGroup": {
                "name": group["name"],
                "title": group["title"],
                "abstractTxt": group["abstract"],
                "mode": "NAMED",
                "publishables": {"published": layers},
            }
        }

        url = "%s/workspaces/%s/layergroups" % (self.url, self._workspace)
        try:
            self.request(url, groupdef, "post")
        except:
            self.request(url, groupdef, "put")

        self.log_info("Group %s correctly created" % group["name"])

    def delete_style(self, name):
        if self.style_exists(name):
            url = "%s/workspaces/%s/styles/%s?purge=true&recurse=true" % (
                self.url,
                self._workspace,
                name,
            )
            r = self.request(url, method="delete")

    def _exists(self, url, category, name):
        try:
            r = self.request(url)
            root = r.json()["%ss" % category]
            if category in root:
                items = [s["name"] for s in root[category]]
            else:
                return False
            return name in items
        except:
            return False

    def layer_exists(self, name):
        url = "%s/workspaces/%s/layers.json" % (self.url, self._workspace)
        return self._exists(url, "layer", name)

    def layers(self):
        url = "%s/workspaces/%s/layers.json" % (self.url, self._workspace)
        r = self.request(url)
        root = r.json()["layers"]
        if "layer" in root:
            return [s["name"] for s in root["layer"]]
        else:
            return []

    def style_exists(self, name):
        url = "%s/workspaces/%s/styles.json" % (self.url, self._workspace)
        return self._exists(url, "style", name)

    def workspace_exists(self):
        url = "%s/workspaces.json" % (self.url)
        return self._exists(url, "workspace", self._workspace)

    def will_delete_layers_on_publication(self, toPublish):
        if self.workspace_exists():
            layers = self.layers()
            toDelete = list(set(layers) - set(toPublish))
            return bool(toDelete)
        else:
            return False

    def datastore_exists(self, name):
        url = "%s/workspaces%s/datastores.json" % (self.url, self._workspace)
        return self._exists(url, "dataStore", name)

    def _delete_datastore(self, name):
        url = "%s/workspaces/%s/datastores/%s?recurse=true" % (
            self.url,
            self._workspace,
            name,
        )
        try:
            r = self.request(url, method="delete")
        except:
            pass

    def delete_layer(self, name, recurse=True):
        if self.layer_exists(name):
            recurse_param = "recurse=true" if recurse else ""
            url = "%s/workspaces/%s/layers/%s.json?%s" % (
                self.url,
                self._workspace,
                name,
                recurse_param,
            )
            r = self.request(url, method="delete")


    def layer_preview_url(self, names, bbox, srs):
        baseurl = self.base_url()
        names = ",".join(["%s:%s" % (self._workspace, name) for name in names])
        url = (
            "%s/%s/wms?service=WMS&version=1.1.0&request=GetMap&layers=%s&format=application/openlayers&bbox=%s&srs=%s&width=800&height=600"
            % (baseurl, self._workspace, names, bbox, srs)
        )
        return url

    def full_layer_name(self, name):
        return "%s:%s" % (self._workspace, name)

    def layer_wms_url(self, name):
        return "%s/wms?service=WMS&version=1.1.0&request=GetCapabilities" % (
            self.baseUrl()
        )

    def layerWfsUrl(self):
        return "%s/wfs" % (self.baseUrl())

    def set_layer_metadata_link(self, name, url):
        layerUrl = "%s/workspaces/%s/layers/%s.json" % (self.url, self._workspace, name)
        r = self.request(layerUrl)
        resourceUrl = r.json()["layer"]["resource"]["href"]
        r = self.request(resourceUrl)
        layer = r.json()
        key = "featureType" if "featureType" in layer else "coverage"
        layer[key]["metadataLinks"] = {
            "metadataLink": [
                {"type": "text/html", "metadataType": "ISO19115:2003", "content": url}
            ]
        }
        r = self.request(resourceUrl, data=layer, method="put")

    def delete_workspace(self):
        if self.workspace_exists():
            url = "%s/workspaces/%s?recurse=true" % (self.url, self._workspace)
            r = self.request(url, method="delete")

    def _publish_style(self, name, style_filename):
        self._ensure_workspace_exists()
        style_exists = self.style_exists(name)
        if style_exists:
            method = "put"
            url = self.url + "/workspaces/%s/styles/%s" % (self._workspace, name)
        else:
            url = self.url + "/workspaces/%s/styles?name=%s" % (self._workspace, name)
            method = "post"
        
        headers = {"Content-type": "application/zip"}
        with open(style_filename, "rb") as f:
            self.request(url, f.read(), method, headers)


    def _set_layer_style(self, layername, stylename):
        url = "%s/workspaces/%s/layers/%s.json" % (self.url, self._workspace, layername)
        r = self.request(url)
        layer = r.json()
        style_url = "%s/workspaces/%s/styles/%s.json" % (
            self.url,
            self._workspace,
            stylename,
        )
        layer["layer"]["defaultStyle"] = {"name": stylename, "href": style_url}
        r = self.request(url, data=layer, method="put")

    def _ensure_workspace_exists(self):
        if not self.workspace_exists():
            url = "%s/workspaces" % self.url
            ws = {"workspace": {"name": self._workspace}}
            self.request(url, data=ws, method="post")

    # ensure that the geoserver we are dealing with is at least 2.13.2
    def check_min_geoserver_version(self, errors):
        try:
            url = "%s/about/version.json" % self.url
            result = self.request(url).json()["about"]["resource"]
        except:
            errors.add(
                "Could not connect to Geoserver.  Please check the server settings (including password)."
            )
            return
        try:
            ver = next(
                (x["Version"] for x in result if x["@name"] == "GeoServer"), None
            )
            if ver is None:
                return  # couldnt find version -- dev GS, lets say its ok
            ver_major, ver_minor, ver_patch = ver.split(".")

            if int(ver_minor) <= 13:  # old
                errors.add(
                    "Geoserver 2.14.0 or later is required. Selected Geoserver is version '"
                    + ver
                    + "'.  Please see <a href='https://my.geocat.net/knowledgebase/100/Bridge-4-compatibility-with-Geoserver-2134-and-before.html'>Bridge 4 Compatibility with Geoserver 2.13.4 and before</a>"
                )
        except:
            # version format might not be the expected. This is usually a RC or dev version, so we consider it ok
            pass


