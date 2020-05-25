import traceback

from bridgehub.apiconstants import VECTORFILE, POSTGIS
from bridgehub.servers import server_from_definition

def publish_project(project):
    results = {}

    geodata_server = server_from_definition(project["servers"]["data"])
    metadata_server = server_from_definition(project["servers"]["metadata"])

    onlysymbology = project["onlysymbology"]
    
    if geodata_server is not None:
        geodata_server.set_project_name(project["name"])
        geodata_server.prepare_for_publishing(onlysymbology)

    layers = project["layers"]

    for layer in layers:
        warnings, errors = [], []        
        #warnings.extend(validateLayer(layer))        
        if geodata_server is not None:
            try:
                geodata_server.reset_log()                
                geodata_server.publish_style(layer["name"], layer["style"]["geostyler"], layer["style"]["icons"])                
            except:            
                errors.append(traceback.format_exc())
            try:
                if not onlysymbology:     
                    geodata_server.publish_layer(layer["name"], layer["data"]["sourcetype"], layer["data"]["source"], layer["fields"])
                    if metadata_server is not None:
                        url = metadata_server.metadata_url(layer["id"])
                        geodata_server.set_layer_metadata_link(layer["name"], url)            
            except:                
                errors.append(traceback.format_exc())        
        if metadata_server is not None:
            try:
                metadata_server.reset_log()
                if geodata_server is not None:
                    fullName = geodata_server.full_layer_name(
                        layer["name"]
                    )
                    wms = geodata_server.layer_wms_url(layer["name"])
                    if layer["data"]["sourcetype"] in [VECTORFILE, POSTGIS]:
                        wfs = geodata_server.layer_wfs_url()
                    else:
                        wfs = None
                else:
                    wms = None
                    wfs = None
                    fullName = None
                metadata_server.publish_layer_metadata(
                    layer["metadata"], wms, wfs, fullName
                )

            except:
                errors.append(traceback.format_exc())

        if geodata_server is not None:
            w, e = geodata_server.logged_info()
            warnings.extend(w)
            errors.extend(e)
        if metadata_server is not None:
            w, e = metadata_server.logged_info()
            warnings.extend(w)
            errors.extend(e)
        results[layer["name"]] = {"warnings": list(set(warnings)), 
                                    "errors": list(set(errors))}

    if geodata_server is not None:
        try:
            geodata_server.create_groups(project["groups"])
        except:
            # TODO: figure out where to put a warning or error message for this
            pass
        finally:
            geodata_server.close_publishing()


    return {"report": results}

