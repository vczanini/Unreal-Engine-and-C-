#!/usr/bin/python

import Config
import EikonalInterfaceLayer
import GetPaths
import os
import sys
import time
import traceback

class Tests(object):

    def __init__(self):

        self.Paths = GetPaths.GetPaths()

        self.Configurator = Config.Config(FilePath = self.Paths.Get("CONFIG_FILEPATH"))

        self.Interface = EikonalInterfaceLayer.Interface(False)

        self.SystemList = []

        # Some lens systems are not yet compatible with Eikonal+:

        blacklist = [
                     '550401',
                     '570415',
                     '570416',
                     '750619',
                     '790224',
                     '900920',
                     '920120',
                     '970860',
                     'MIS002',
                     'MIS006',
                     'MIS007',
                    ]

        LIBLST=open("test-data-1/LIBLST.DBS").readlines()
        for line in LIBLST:
            LineFields = line.split(' ')

            if not LineFields[0] in blacklist:

               self.SystemList.append(LineFields[0])

    def Stop(self):

        self.Interface.Stop()

    def Command(self,message):

        self.Interface.Command(message)

    def LoadSystem(self,FileName):
        """ TODO: figure out how to test this
        """

        self.Interface.LoadSystem(str(FileName))

    def GetNumSurfaces(self,ConfigurationNumber):

        TrueDataPath = os.path.join( os.path.realpath(os.path.join(self.Paths.Get("EXECUTABLE_DIR"),"../test-data-1/GetNumSurfaces")), str('SystemNumSurfaces.true'))
        TrueData=open(TrueDataPath).readlines()
        for line in TrueData:
            LineFields = line.split(': ')
            self.Interface.LoadSystem(str(LineFields[0] + '.DBS'))
            NumSurfaces= self.Interface.GetNumSurfaces(int(ConfigurationNumber))
            if NumSurfaces != int(LineFields[1]):
                print("Error in GetNumSurfaces for system: "+LineFields[0])
                return False
        print("GetNumSurfaces tests finished")
        return True

    def GetSurfaces(self,ConfigurationNumber):
        """ Testing GetSurfaces routine from Interface
        """

        testLen = 50

        for system in self.SystemList:
            self.Interface.LoadSystem(str(system + '.DBS'))
            SystemSurfaces=self.Interface.GetSurfaces(int(ConfigurationNumber))

            TrueDataPath = os.path.join( os.path.realpath(\
                    os.path.join(self.Paths.Get("EXECUTABLE_DIR"),\
                    "../test-data-1/GetSurfaces/SystemSurfaces_20161118")),\
                    str('SystemSurfaces_'+system+'.True'))
            TrueData=open(TrueDataPath).read()

            TrueList = eval(TrueData)
            assert(len(TrueList) == len(SystemSurfaces))

            for i in range(len(TrueList)):
                if TrueList[i] != SystemSurfaces[i]:
                    print('Discrep:\n'
                          'True: {}\n'
                          'Test: {}\n'.format(TrueList[i],SystemSurfaces[i]))
                    return False
        print("GetSurfaces tests finished")
        return True

    def GetRays(self,Wavelength,FieldPoints,PupilPoints):
        """ Testing GetRays routine from Interface

        """
        for system in self.SystemList:
            self.Interface.LoadSystem(str(system + '.DBS'))
            SystemRays=self.Interface.GetRays(Wavelength,FieldPoints,PupilPoints)

            TrueDataPath = os.path.join( os.path.realpath(os.path.join(self.Paths.Get("EXECUTABLE_DIR"),"../test-data-1/GetRays/SystemRays_20161118")), str('SystemRays_'+system+'.True'))
            TrueData=open(TrueDataPath).read()
            TrueList = eval(TrueData)

            for i in range(len(TrueList)):
                if TrueList[i] != SystemRays[i]:
                    print('Discrep:\n'
                          'True: {}\n'
                          'Test: {}\n'.format(TrueList[i],SystemRays[i]))
                    return False
        print("GetRays tests finished")
        return True

if __name__ == "__main__":

    TheTest = Tests()

    print("Running Tests")

    if TheTest.GetSurfaces(0) == False:
        print("Error in GetSurfaces :(!")
    if TheTest.GetNumSurfaces(0) == False:
        print("Error in GetNumSurfaces :(!")
    if TheTest.GetRays(1,0,10) == False:
        print("Error in GetRays :(!")


    print("Tests finished!")
    TheTest.Stop()
