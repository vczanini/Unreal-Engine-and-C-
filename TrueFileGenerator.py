#!/usr/bin/python

from Queue import Queue
import Config
import EikonalInterfaceLayer
import GetPaths
import os
import sys
import time
import traceback
from os.path import dirname, abspath

class TrueFileGenerator(object):

    def __init__(self):

        self.Paths = GetPaths.GetPaths()

        self.Configurator = Config.Config(FilePath = self.Paths.Get("CONFIG_FILEPATH"))

        self.Interface = EikonalInterfaceLayer.Interface(True)

        self.SystemList = []

        LIBLST=open("test-data-1/LIBLST.DBS").readlines()
        for line in LIBLST:
            LineFields = line.split(' ')
            if LineFields[0] != 'MIS002':
                self.SystemList.append(LineFields[0])

        # print self.SystemList


    def Stop(self):

        self.Interface.Stop()

    # def Command(self,message):

    #     self.Interface.Command(message)

    # def LoadSystem(self,FileName):
    #     """ Asks the interface layer to load a .A system file

    #     """
        
    #     self.Interface.LoadSystem(str(FileName))

    def GetNumSurfacesTrueFile(self,ConfigurationNumber):
        GetNumSurfacesTestPath = os.path.realpath(os.path.join(TheGenerator.Paths.Get("EXECUTABLE_DIR"),"../test-data-1/GetNumSurfaces"))
        TrueFilePath = os.path.join(GetNumSurfacesTestPath, str('SystemNumSurfaces.true'))
        TrueFile = open(TrueFilePath,'w')
        numSurfacesList = ""
        for system in self.SystemList:
            self.Interface.LoadSystem(str(system + '.DBS'))
            numSurfaces = self.Interface.GetNumSurfaces(int(ConfigurationNumber))
            numSurfacesList = numSurfacesList + str(system+': '+str(numSurfaces) + '\n')
        TrueFile.write(numSurfacesList)
        

    def GetSurfacesTrueFiles(self,ConfigurationNumber):
        for system in self.SystemList:
            self.Interface.LoadSystem(str(system + '.DBS'))
            surfaces = self.Interface.GetSurfaces(int(ConfigurationNumber))
            GetSurfacesTestPath = os.path.realpath(os.path.join(TheGenerator.Paths.Get("EXECUTABLE_DIR"),"../test-data-1/GetSurfaces"))
            SystemSurfacesPath = os.path.join(GetSurfacesTestPath, "SystemSurfaces_"+str(time.strftime("%Y%m%d")))
            if not os.path.exists(SystemSurfacesPath):
                os.makedirs(SystemSurfacesPath)
            TrueFilePath = os.path.join(SystemSurfacesPath, str('SystemSurfaces_'+system+'.True'))
            TrueFile = open(TrueFilePath,'w')
            TrueFile.write(str(surfaces))



    def GetRaysTrueFiles(self,Wavelength,FieldPoints,PupilPoints):
        for system in self.SystemList:
            self.Interface.LoadSystem(str(system + '.DBS'))
            rays = self.Interface.GetRays(int(Wavelength),int(FieldPoints),int(PupilPoints))
            GetRaysTestPath = os.path.realpath(os.path.join(TheGenerator.Paths.Get("EXECUTABLE_DIR"),"../test-data-1/GetRays"))
            SystemRaysPath = os.path.join(GetRaysTestPath, "SystemRays_"+time.strftime("%Y%m%d"))
            if not os.path.exists(SystemRaysPath):
                os.makedirs(SystemRaysPath)
            TrueFilePath = os.path.join(SystemRaysPath, str('SystemRays_'+system+'.True'))
            TrueFile = open(TrueFilePath,'w')
            TrueFile.write(str(rays))


    

if __name__ == "__main__":

    TheGenerator = TrueFileGenerator()
    TheGenerator.GetSurfacesTrueFiles(0)
    TheGenerator.GetRaysTrueFiles(1,0,10) 

    TheGenerator.GetNumSurfacesTrueFile(0)
    
    TheGenerator.Stop()
    
    
