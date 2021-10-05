import sys
try:
    import configparser
except:
    print("\nThe module ConfigParser is not installed.")
    print("You can install it using")
    print("  sudo -H pip install ConfigParser\n")
    # Exit with an error code.
    sys.exit(1)


class Config(object):

    """

    """

    def __init__(self,FilePath=None):

        self.TheConfigParser = configparser.SafeConfigParser(allow_no_value=True)

        # If the config file path was already given, load it.

        if not FilePath==None:
            self.LoadConfig(FilePath)


    def WriteConfig(self,FilePath):

        """ Not implemented: Writes *USER* Config file, not for master Config.
        """

        pass

    def LoadConfig(self,FilePath):

        """ Loads the config file

        """

        try:
            self.TheConfigParser.read(FilePath)
        except:
            # Don't store the file name.  The full traceback of the exception
            # can be accessed using the "traceback" module.
            ErrorMessage = traceback.format_exc()
            print(ErrorMessage)
            theErrorHandler.nonFatalError("Could not read Config file " + FilePath + ErrorMessage)
            self.IsLoaded = False
            return -1
        else:
            # If successful, store the filename.
            self.ConfigFileName = FilePath
            self.IsLoaded = True
            return 0

    def Get(self,Section,Option):
        """ Return original value from config file (string)

        """

        try:
            return self.TheConfigParser.get(Section,Option)
        except:
            return None

    def GetInt(self,Section,Option):

        """ Type-specific convenience 'get' method

        Returns the correct type if the setting is found.  If the setting is
        not found or cannot be recast as the correct type, returns None.

        """

        try:
            return self.TheConfigParser.getint(Section,Option)
        except:
            return None

    def GetFloat(self,Section,Option):

        """ Type-specific convenience 'get' method

        Returns the correct type if the setting is found.  If the setting is
        not found or cannot be recast as the correct type, returns None.

        """

        try:
            return self.TheConfigParser.getfloat(Section,Option)
        except:
            return None

    def GetBoolean(self,Section,Option):

        """ Type-specific convenience 'get' method

        Returns the correct type if the setting is found.  If the setting is
        not found or cannot be recast as the correct type, returns None.

        """

        try:
            return self.TheConfigParser.getboolean(Section,Option)
        except:
            return None

    def GetItems(self,Section):

        """ Non-type-specific, returns a *section* of the config

        If the section is not found, return None.

        """

        try:
            return self.TheConfigParser.items(Section)
        except:
            traceback.print_exc()
            return None

    def GetSetting(self,Section,Option):

        """ Non-type-specific get-method for completeness

        If the setting is not found, returns None.

        """

        self.TheConfigParser.get(Section,Option)

        try:
            return self.TheConfigParser.get(Section,Option)
        except:
            return None
