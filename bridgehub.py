# This file serves as a bootstrapper for the executable created by PyInstaller.
# It is required whenever make.bat is being run.

from bridgehub import hub

if __name__ == '__main__':
    hub.main()
