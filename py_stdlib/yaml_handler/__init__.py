import os
import yaml

class FileDoesNotExist(Exception):
    """File does not exist exception

    @note: Include the file name in the full_path
    @ivar full_path: The full path to the missing file.  Includes the file name
    """
    def __init__(self, full_path):
        message = "The file, %s, does not exist." % full_path
        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, message)

def load_config(config_file):
    if not os.path.exists(config_file): 
        raise FileDoesNotExist(config_file)

    config = yaml.load(file(config_file, 'r'))

    return config
