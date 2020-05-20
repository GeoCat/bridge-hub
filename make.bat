@ECHO OFF

SET dist_dir=%~f1

IF "%dist_dir%"=="" (
	SET dist_dir=%~dp0dist
)

ECHO PyInstaller Output Path: %dist_dir%
ECHO Running PyInstaller...

pyinstaller --clean -y --distpath %dist_dir% --onefile bridgehub.py

ECHO Copying BridgeHub configuration...

xcopy /y .\bridgehub\config\bridgehub.xml %dist_dir%

ECHO Done