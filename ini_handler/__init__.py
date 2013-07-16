import os
import ConfigParser


class Ini(object):
    def __init__(self, ini_path):
        if os.path.isfile(ini_path):
            self.cp = ConfigParser.ConfigParser()
            self.cp.read(ini_path)
        else:
            raise "Invalid INI file specified: %s" % ini_path

    def has_option(self, section, option):
        """
        Helper function for ConfigParser objects to determine if a particular 
        section has the specified option.

        @param section: Section of config parser to read
        @type section: str
        @param option: Option in section to retrieve
        @type option: str
        @returns: Boolean describing whether or not the option exists in the 
            specfied section
        @rtype: Bool
        """
        return self.cp.has_option(section, option)

    def get(self, section, option, default=""):
        """
        Helper function for ConfigParser objects which allows setting the default.

        ConfigParser objects throw an exception if one tries to access an option
        which does not exist; this catches the exception and returns the default
        value instead.

        @param section: Section of config parser to read
        @param option: Option in section to retrieve
        @param default: Default value if the section/option is not present.
        @returns: Value stored in CP for section/option, or default if it is not
            present.
        """
        try:
            return self.cp.get(section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default

    def getBoolean(self, section, option, default=True):
        """
        Helper function for ConfigParser objects which allows setting the default.
    
        If the cp object has a section/option of the proper name, and if that value
        has a 'y' or 't', we assume it's supposed to be true.  Otherwise, if it
        contains a 'n' or 'f', we assume it's supposed to be true.
        
        If neither applies - or the option doesn't exist, return the default
    
        @param section: Section of config parser to read
        @param option: Option in section to retrieve
        @param default: Default value if the section/option is not present.
        @returns: Value stored in CP for section/option, or default if it is not
            present.
        """
        val = str(self.get(section, option, default)).lower()
        if val.find('t') >= 0 or val.find('y') >= 0 or val.find('1') >= 0:
            return True
        if val.find('f') >= 0 or val.find('n') >= 0 or val.find('0') >= 0:
            return False
        return default