import os
import sys

class GetPaths(object):

# Set some directories, based on where the this process's executable is
# found.

    def __init__(self):

        self.Paths = {}

        try:
            self.Paths["EXECUTABLE_DIR"] = sys.path[0]
        except:
            print("\nCould not find the location of this executable.\n")
            traceback.print_exc()
            sys.exit(1)

        # Set the configuration file, path, based on the location of this
        # executable.

        try:
            self.Paths["CONFIG_DIR"] = os.path.normpath(os.path.join(self.Paths["EXECUTABLE_DIR"],'../config'))
        except:
            print("\nCould not set the configuration directory\n")
            sys.exit(1)

        try:
            self.Paths["CONFIG_FILEPATH"] = os.path.join(self.Paths["CONFIG_DIR"],'Config')
        except:
            print("\nCould not set the configuration filepath\n")
            sys.exit(1)

        try:
            self.Paths["RUN_DATA_DIR"]    = os.path.normpath(os.path.join(self.Paths["EXECUTABLE_DIR"],'../rundata'))
            if not os.path.exists(self.Paths["RUN_DATA_DIR"]):
                os.mkdir(self.Paths["RUN_DATA_DIR"])
        except:
            print("\nCould not set the rundata directory\n")
            sys.exit(1)

    def Get(self,path):

        if path in self.Paths.keys():
            return self.Paths[path]
        else:
            return None

