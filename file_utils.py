import bpy
import os

def get_default_output_directory():
    return os.path.join(bpy.context.preferences.filepaths.temporary_directory, 'lightfield')

def get_default_path_config_file():
    return os.path.join(get_default_output_directory(), 'lightfield.cfg')
