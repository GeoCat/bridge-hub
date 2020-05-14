set targetdir=%~dp0.
pyinstaller --clean -y --distpath %targetdir% --onefile bridgeserver.py
xcopy /y .\bridgeserver\config\bridgeserver.xml %targetdir%