import bpy
import os

def get_default_output_directory():
    path = os.path.join(
        bpy.context.preferences.filepaths.temporary_directory, 'lightfield')
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_default_path_config_file():
    return os.path.join(get_default_output_directory(), 'lightfield.cfg')