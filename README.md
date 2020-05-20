# GeoCat Bridge Hub

A microserver application to expose the bridge-style library.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)

Check the [OpenAPI definition](bridgehub/swagger.json) to know more about the API.

## Local Hub for ArcGIS Users
It is possible to run the hub locally as a standalone executable. This option is particularly useful for ArcGIS users on Windows.

In order to build the executable, you need to install [PyInstaller](https://pypi.org/project/PyInstaller) first.  
Once this is done, you can `cd` into the project folder and call the `make.bat` file, optionally with a destination folder argument.   
If no arguments are specified, PyInstaller will output the `bridgehub.exe` to a `dist` folder in the current directory.  
