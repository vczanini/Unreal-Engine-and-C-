#!/usr/bin/python

from Queue import Queue
import Config
import EikonalInterfaceLayer
import GetPaths
import os
import sys
import time
import traceback

class MatlabAPI(object):

    def __init__(self):

        self.Paths = GetPaths.GetPaths()

        self.Configurator = Config.Config(FilePath = self.Paths.Get("CONFIG_FILEPATH"))

        self.Interface = EikonalInterfaceLayer.Interface(True)

    def Stop(self):

        self.Interface.Stop()

    def Command(self,message):

        self.Interface.Command(message)

    def LoadSystem(self,FileName):
        """ Asks the interface layer to load a .A system file

        """
        
        self.Interface.LoadSystem(str(FileName))

    def GetNumSurfaces(self,ConfigurationNumber):
        """ Asks the interface layer for the number of surfaces.

        Returns an integer.

        """

        return self.Interface.GetNumSurfaces(int(ConfigurationNumber))

    def GetSurfaces(self,ConfigurationNumber):
        """ Asks the interface layer for the list of surfaces.

        This is a list of mixed-type values, but maybe should be a list of
        dicts for easy lookup.

        """

        return self.Interface.GetSurfaces(int(ConfigurationNumber))

    def GetRays(self,Wavelength,FieldPoints,PupilPoints):
        """ Asks the interface layer for the list of rays.

        """

        return self.Interface.GetRays(int(Wavelength),int(FieldPoints),int(PupilPoints))


    

if __name__ == "__main__":

    TheAPI = MatlabAPI()
    
    TheAPI.LoadSystem("TRIPLET.A")
    SystemRays=TheAPI.GetRays(1,0,3)
    f=open("SystemRays.true", 'w')
    f.write(str(SystemRays))


    print "Stopping the MatlabAPI..."
    TheAPI.Stop()
    
    
