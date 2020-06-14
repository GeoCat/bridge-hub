import os
import shutil
import uuid
import tempfile

def temp_folder():
    path = os.path.join(tempfile.gettempdir(), "bridgehub")
    os.makedirs(path, exist_ok=True)    
    return path

def temp_folder_in_temp_folder():    
    folder = os.path.join(temp_folder(), str(uuid.uuid4()).replace("-", ""))
    os.makedirs(folder, exist_ok=True)    
    return folder

def temp_filename_in_temp_folder(basename):
    folder = temp_folder_in_temp_folder()    
    filename = os.path.join(folder, basename)        
    return filename

def remove_temp_folder():
    shutil.rmtree(tempFolder())
