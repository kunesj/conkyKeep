#!/usr/bin/python3
#coding: utf-8

# how to import:
# from config_manager import CONFIG_MANAGER

import pkg_resources
import configparser

class ConfigManager(object):
    DEFAULT_CFG_PATH = pkg_resources.resource_filename(__name__, "config_default.cfg")

    def __init__(self):
        self.config = None
        self.clearConfig()

    @classmethod
    def getObject(cls):
        return cls()

    def clearConfig(self):
        self.config = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=('#',))
        # make case sensitive
        self.config.optionxform = lambda option: option

        try:
            self.config.read(self.DEFAULT_CFG_PATH, encoding="utf-8")
        except Exception:
            print("Couldn't load default config file '%s'!" % self.DEFAULT_CFG_PATH)

    def loadConfig(self, path, update=True):
        if not update:
            self.clearConfig()

        try:
            self.config.read(path, encoding="utf-8")
        except Exception:
            print("Couldn't load config file '%s'!" % path)

    def get(self, section, option, lowercase=False):
        val = self.config.get(section, option)
        if type(val) == type([]): # remove list container
            val = val[0]
        if lowercase:
            val = val.lower()
        return val

    def getBoolean(self, section, option):
        return self.config.getboolean(section, option)

    def getInt(self, section, option):
        str_num = self.get(section, option).strip()
        if str_num.startswith("0x"):
            return int(str_num, 16)
        else:
            return self.config.getint(section, option)

    def getFloat(self, section, option):
        return self.config.getfloat(section, option)

    def getList(self, section, option, lowercase=False):
        str_list = [ x.strip() for x in self.get(section, option, lowercase=lowercase).strip().split(",") ]
        return str_list

    def getListInt(self, section, option):
        return [ int(x) for x in self.getList(section, option) ]

    def getListFloat(self, section, option):
        return [ float(x) for x in self.getList(section, option) ]

    def sections(self):
        return self.config.sections()

    def hasSection(self, section):
        return  self.config.has_section(section)

    def options(self, section):
        return self.config.options(section)

    def hasOption(self, section, option):
        return self.config.has_option(section, option)

CONFIG_MANAGER = ConfigManager.getObject()


if __name__ == "__main__":
    print(CONFIG_MANAGER.sections())
    print(CONFIG_MANAGER.options("Login"))
    print([CONFIG_MANAGER.getListInt("Style", "FontColor")])
