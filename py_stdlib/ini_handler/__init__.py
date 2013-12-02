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
        Helper function for ConfigParser objects which allows converts values to
        Booleans.  The default value is returned if the value is not one of the 
        following:
            Valid "True" values:  ['true', '1', 't', 'y', 'yes']
            Valid "False" values: ['false', '0', 'f', 'n', 'no']

        @param section: Section of config parser to read
        @param option: Option in section to retrieve
        @param default: Default value if the section/option is not present.
        @returns: Value stored in CP for section/option, or default if it is not
            present.
        """
        val = str(self.get(section, option, default)).lower()
        if val in ['true', '1', 't', 'y', 'yes']: return True
        if val in ['false', '0', 'f', 'n', 'no']: return False
        return default

    def getlist(self, section, option):
        """
        Helper function for ConfigParser objects which allows converts values to
        a list.  For example the following ini file defines a '\n' delimited 
        string that can be converted to a list via the splitlines function.
        ;test.ini
        [hello]
        barlist = 
            item1
            item2

        The value of config.get('hello','barlist') will be: "\nitem1\nitem2"

        @param section: Section of config parser to read
        @param option: Option in section to retrieve
        @returns: List built from value stored in CP for section/option.
        """
        value = self.cp.get(section, option)
        return list(filter(None, (x.strip() for x in value.splitlines())))

    def getlistint(self, section, option):
        """
        Helper function for ConfigParser objects which allows converts values to
        a list of integers.

        @param section: Section of config parser to read
        @param option: Option in section to retrieve
        @returns: List of integers built from value stored in CP for section/option.
        """
        return [int(x) for x in self.getlist(section, option)]
