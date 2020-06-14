# GeoCat Bridge Hub

A microserver application to publish data and metadata to different servers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

Check the [OpenAPI definition](bridgehub/swagger.yaml) to know more about the API.

## Starting the server

To start the server, run

``$ python bridgehub.py``

## Using the command line version

If you want to process a project definition stored in a file, instead of starting the Bridgehub server, run

``$ python bridgehub.py -f [path/to/project/file]``

The file should contain a JSON description of the project, just like the JSON you would post to the ``/publish`` endpoint. Se the API definition to know more about the format of the JSON project description.

## Local Hub for ArcGIS Users
It is possible to run the hub locally as a standalone executable. This option is particularly useful for ArcGIS users on Windows.

In order to build the executable, you need to install [PyInstaller](https://pypi.org/project/PyInstaller) first.  
Once this is done, you can `cd` into the project folder and call the `make.bat` file, optionally with a destination folder argument.   
If no arguments are specified, PyInstaller will output the `bridgehub.exe` to a `dist` folder in the current directory.  
