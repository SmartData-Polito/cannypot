import configparser
from os.path import abspath, dirname, exists, join

class ExplorerConfig(object):
    __instance = None

    def __new__(cls):
        if ExplorerConfig.__instance is None:
            ExplorerConfig.__instance = object.__new__(configparser.ConfigParser)
            ExplorerConfig.__instance.__init__(interpolation=configparser.ExtendedInterpolation())
            ExplorerConfig.__instance.read(get_config_path())
        return ExplorerConfig.__instance

def get_config_path():
    """
    Get absolute path to the config file
    """
    config_files = ["etc/explorer.cfg"]
    found_confs = [path for path in config_files if exists(path)]

    if found_confs:
        return found_confs

    print("Config file not found")
