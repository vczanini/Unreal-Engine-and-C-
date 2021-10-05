#!/usr/bin/python

from re import T
import Config
import Core
import GetPaths
import System
import os
import shlex
import subprocess
import sys
import time
import re
import zmq
import numpy as np
import enum



class Core(object):

    Endings = ['<END>','<WAITING>','<READY>']

    # Default is to not echo to the terminal.
    echo = True

    def __init__(self):

        self.Paths = GetPaths.GetPaths()

        self.daemon           = True
        self.receive_messages = True

        self.Configurator   = Config.Config(FilePath = self.Paths.Get("CONFIG_FILEPATH"))
        self.RunDataDir     = self.Paths.Get("RUN_DATA_DIR")

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5556")



        if not os.path.exists(self.RunDataDir):
            os.mkdir(self.RunDataDir)

        self.StartEikonal()
        self.run()
        self.socket.close()
        self.context.term()

        print("Exited")

    def SetEcho(self,echo):
        """ Turn on/off the echo to terminal

        Returns the new status of self.echo (True/False)

        """

        if echo[0] == 'on':
            self.echo = True
        else:
            self.echo = False

        return self.echo

    def PrintToStdout(self,string):
        """ For debugging, print the string to stdout

        Returns True.

        """

        print(string)
        return True

    def run(self):

        while True:
            val = self.socket.recv_string()
            if (self.echo):
                print(val)
            valFields = val.split(' ')
            if val == "Stop":   # If you send `Stop`, exit.
                self.EikSubprocess.stdin.write(b"x\n")
                self.EikSubprocess.stdin.flush()
                self.socket.send_pyobj("Exit")
                print("Exiting...")
                return

            elif valFields[0] == "GetNumSurfaces":
                self.socket.send_pyobj(self.GetNumSurfaces(int(valFields[1])))

            elif valFields[0] == "GetSurfaces":
                self.socket.send_pyobj(self.GetSurfaces(int(valFields[1])))

            elif valFields[0] == "GetSurfacesGlobal":
                self.socket.send_pyobj(self.GetSurfacesGlobal(*valFields[1:]))

            elif valFields[0] == "GetRays":

                self.socket.send_pyobj(self.GetRays(int(valFields[1]),int(valFields[2]),int(valFields[3])))

            elif valFields[0] == "LoadSystem":
                self.LoadSystem(valFields[1])
                self.socket.send_pyobj("System Loaded: %s " % valFields[1])

            elif valFields[0] == "InsSur":
                response = self.InsSur(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "InsZerSur":
                response = self.InsZerSur(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "InsApeSto":
                response = self.InsApeSto(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "ChaApeSto":
                response = self.ChaApeSto(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "ParEntPup":
                response = self.ParEntPup(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "ChaReflecSur":
                response = self.ChaReflecSur(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "ChaRefracSur":
                response = self.ChaRefracSur(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "ChaZerSur":
                response = self.ChaZerSur(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "RemSur":
                response = self.RemSur(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "ChaRefereSur":
                response = self.ChaRefereSur(valFields[1:])
                self.socket.send_pyobj(response)
                
            elif valFields[0] == "SurMov":
                response = self.SurMov(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SurTil":
                response = self.SurTil(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "GetSurfaceDataTable":
                response = self.GetSurfaceDataTable(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "GetFirstOrderParameter":
                response = self.GetFirstOrderParameter(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SlideAndRayTrace":
                response = self.SlideAndRayTrace(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SetParameter":
                response = self.SetParameter(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "InsertFieldPoint":
                response = self.InsertFieldPoint(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "RemoveFieldPoint":
                response = self.RemoveFieldPoint(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "ListFieldPoints":
                response = self.ListFieldPoints(valFields[1])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SetImageDistanceSolve":
                response = self.SetImageDistanceSolve(valFields[1:])
                self.socket.send_pyobj(response)
                
            elif valFields[0] == "SetRotSym":
                response = self.SetRotSym(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SetAbeSym":
                response = self.SetAbeSym(valFields[1:])
                self.socket.send_pyobj(response)  

            elif valFields[0] == "ChaSysCla":
                response = self.ChaSysCla(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "GetGenSysSet":
                response = self.GetGenSysSet(valFields[1])
                self.socket.send_pyobj(response)

            elif valFields[0] == "GetWavelengths":
                response = self.GetWavelengths(valFields[1])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SetWavelengths":
                response = self.SetWavelengths(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SaveSystem":
                response = self.SaveSystem(*valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SetEcho":
                response = self.SetEcho(valFields[1:])
                self.socket.send_pyobj(response)

            elif valFields[0] == "PrintToStdout":
                response = self.PrintToStdout(val.split(' ',1)[1])
                self.socket.send_pyobj(response)

            elif valFields[0] == "SpeedTest":
                self.socket.send_pyobj(val)

            else:
                self.EikSubprocess.stdin.write(bytes(val+"\n",'ascii'))
                self.EikSubprocess.stdin.flush()
                output = self.RecvResponse(echo=self.echo)
                self.socket.send_pyobj(output)

    def RecvResponse(self,echo = None):
        """ Currently, we are getting the responses from a pipe using 'read'
        """

        if echo == None:
            echo = self.echo

        OutputList = []
        output = ""
        NullStringCounter = 0

        TheEnd = False
        while not TheEnd:

            output = self.EikSubprocess.stdout.readline()

            # The Python3 version of subprocess returns bytes objects instead
            # of strings.  We will always decode to ascii, since the responses
            # from Eikonal are strings.

            OutputList.append(output.decode('ascii'))

            # See if one of the endings ("<END>, etc.") is in this output line.

            for one in self.Endings:

                if one in str(output):

                    TheEnd = True
                    break

        if echo:
            print("Received from Eikonal:", end=' ')
            for one in OutputList:
                print(one.strip())

        return OutputList

    def StartEikonal(self):
        """ Start the Eikonal process, read the welcome message from eikonal

        Sends the '.' command to set the working directory.

        """

        # Get the eikonal executable name from the config.

        self.EikonalExecutable = self.Configurator.GetSetting(
                      Section="Paths",Option="EikonalExecutable"
                     )

        # We will tell Eikonal to redirect its output (stdout) to this file.

        EikonalCommand = self.EikonalExecutable

        EikonalCommandArgs = shlex.split(EikonalCommand)

        #Start the Eikonal process.

        self.EikSubprocess = subprocess.Popen(
                            EikonalCommandArgs,
                            shell=False,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            )


        # Set the directory and try some commands.

        # Get the welcome message.  Otherwise, it will interfere with the
        # parsing the output from the first command.

        self.RecvResponse(echo=self.echo)

        self.EikSubprocess.stdin.write(b".\n")
        self.EikSubprocess.stdin.flush()
        self.RecvResponse(echo=self.echo)

        if self.echo:
            print("\n")

        return

    def LoadSystem(self,FileName):
        """ Loads a system .A file in the Eikonal back end.
        """

        self.EikSubprocess.stdin.write(bytes("loasys {} \n".format(FileName),'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(echo=self.echo)

        return None

    def GetNumSurfaces(self,ConfigurationNumber,skip=[]):
        """ Return an integer number of surfaces in the current configuration

        (Configuration here means a configuration of the lens system in the
        back end.  Refer to the Eikonal+ back end docs, or the original Eikonal
        manual.)

        skip is a list containing types of surface to be ignored when counting 
        number of surfaces 
        """
        SurfaceList = self.GetSurfaces(ConfigurationNumber)
        if not skip:
            return len(SurfaceList)

        CountSurfaces = 0
        for Surface in SurfaceList:
            if not Surface['TypeCode'] in skip:
                CountSurfaces += 1

        return CountSurfaces

    def GetSurfaces(self,ConfigurationNumber):
        """ Return the surfaces in the loaded lens system in dict format

        This parses the text out put from the Eikonal+ back end and produces a
        dictionary of surfaces.

        The output of LISSUR is combined with the output of SYSDAT.

        lissur 0
         //   Type |   Curvature | Dist to next   | Refr indx | Gls code | Glass
         //----------------------------------------------------------------------
            0 SP      0.00000000      1.00000000    1.000000      0.000
            1 SP      0.12987013      0.50000000    1.376000      0.000
            2 AS      0.00000000      0.00000000    1.376000      0.000
            3 SP      0.14705882      2.00000000    1.336000      0.000
            4 ZR      0.29411765      3.00000000    1.518722   6517.642   BK7
            5 SP      0.10000000      0.54600000    1.386000      0.000
            6 SP      0.12640627      2.41900000    1.406000      0.000
            7 SP     -0.17361111      0.63500000    1.386000      0.000
            8 SP     -0.16666667     17.20000000    1.336000      0.000
            9 SP      0.00000000      0.00000000    1.000000      0.000
         <END>
        sysdat
         // S# | Type |    Curvature |     Thickness |  Y Semi-aper. |     N1 |      N2 |      N3 |  Gl Code | Type |
         //----+------+--------------+---------------+---------------+--------+---------+---------+----------+------+
              0  SP        0.00000000      1.00000000      0.00000000   1.0000    1.0000    1.0000      0.0000      0 Ref Sfce
              1  SP        0.12987013      0.50000000      2.00000000   1.3760    1.3760    1.3760      0.0000      4 Sphere
              2  AS        0.00000000      0.00000000      1.98279720   1.3760    1.3760    1.3760      0.0000      3 Ap Stop
              3  SP        0.14705882      2.00000000      1.96169880   1.3360    1.3360    1.3360      0.0000      4 Sphere
              4  ZR        0.29411765      3.00000000      0.00000000   1.5187    1.5228    1.5147   6517.6420      4
              5  SP        0.10000000      0.54600000      1.76506950   1.3860    1.3860    1.3860      0.0000      4 Sphere
              6  SP        0.12640627      2.41900000      1.72435060   1.4060    1.4060    1.4060      0.0000      4 Sphere
              7  SP       -0.17361111      0.63500000      1.57884850   1.3860    1.3860    1.3860      0.0000      4 Sphere
              8  SP       -0.16666667     17.20000000      1.52769510   1.3360    1.3360    1.3360      0.0000      4 Sphere
              9  SP        0.00000000      0.00000000      0.00000000   1.0000    1.0000    1.0000      0.0000      2 Img Plane
         <END>


        """

        self.EikSubprocess.stdin.write(bytes("lissur {}\n".format(ConfigurationNumber),'ascii'))
        self.EikSubprocess.stdin.flush()
        LissurOutput = self.RecvResponse(echo = self.echo)

        SurfaceList = []

        # Find the first line that doesn't start with '//'

        for i in range(len(LissurOutput)):

            ThisLine = LissurOutput[i].strip()
            if self.echo:
                print(ThisLine)

            if ThisLine.startswith('//'):
                # Skip this one.
                continue

            # This is a real line of surface data.  Split on spaces.  The Glass
            # field may be empty.


            LineFields = ThisLine.split()

            if len(LineFields) < 6:
                # This is probably the <END> tag.
                continue


            ThisSurfaceDict = {"SurfaceNumber": int(LineFields[0]),
                               "TypeCode"     : LineFields[1],
                               "Curvature"    : float(LineFields[2]),
                               "DistToNext"   : float(LineFields[3]),
                               "RefrIndex"    : float(LineFields[4]),
                               "GlassCode"    : float(LineFields[5]),
                              }

            # If there is a Glass name, add it.  Otherwise None.

            if len(LineFields) == 7:
               ThisSurfaceDict["GlassName"] = LineFields[6]
            else:
               ThisSurfaceDict["GlassName"] = None

            SurfaceList.append(ThisSurfaceDict)

        # Add the output of SYSDAT to the surface information.

        # // S# | Type |    Curvature |     Thickness |  Y Semi-aper. |     N1 |      N2 |      N3 |  Gl Code | Type |
        # //----+------+--------------+---------------+---------------+--------+---------+---------+----------+------+
        #      0  SP        0.00000000      1.00000000      0.00000000   1.0000    1.0000    1.0000      0.0000      0 Ref Sfce

        self.EikSubprocess.stdin.write(bytes("sysdat\n",'ascii'))
        self.EikSubprocess.stdin.flush()
        SysdatOutput = self.RecvResponse(echo = self.echo)

        for i in range(len(SysdatOutput)):

            ThisLine = SysdatOutput[i].strip()
            if self.echo:
                print(ThisLine)

            if ThisLine.startswith('//'):
                # Skip this one.
                continue

            # This is a real line of surface data.  Split on spaces.  The Glass
            # field may be empty.

            LineFields = ThisLine.split()
            numFields  = len(LineFields)

            if numFields < 10:
                # This is probably the <END> tag.
                continue

            surfaceNumber = int(LineFields[0])
            typeNumber    = int(LineFields[9])
            YSemiAperture = float(LineFields[4])
            N1            = float(LineFields[5])
            N2            = float(LineFields[6])
            N3            = float(LineFields[7])

            if numFields == 11:
                SurfaceList[surfaceNumber]['additionalTypeInfo'] = LineFields[10]

            SurfaceList[surfaceNumber]['typeNumber']    = typeNumber
            SurfaceList[surfaceNumber]['YSemiAperture'] = YSemiAperture
            SurfaceList[surfaceNumber]['N1']            = N1
            SurfaceList[surfaceNumber]['N2']            = N2
            SurfaceList[surfaceNumber]['N3']            = N3

        return SurfaceList

    def GetSurfacesGlobal(self,configurationNumber,referenceSurface):
        """ Return a list of surface dicts, using global coordinates

        This parses the text out put from the Eikonal+ back end and produces a
        dictionary of surfaces.
        
        The global coordinates are produced with respect to the requested
        surface number.

        disglocoo 0 0
        //1
        //        0:BASIC     TRIPLE      23 Apr2012    10:  47:  32
        //        Cooke Triplet f/4.5
        //
        //
        //        TABLE OF GLOBAL COORDINATES: Origin at surface No.  0
        //
        //  X,  Y,  Z : unit vectors at vertex of reference surface
        //  I,  J,  K : unit vectors at vertex of selected surface
        // ISX,....KSZ: projections of selected surface unit vectors over reference
        //              surface unit vectors
        // XXX,YYY,ZZZ: vertex coordinates of selected surface from vertex of
        //              reference surface
        // NOTE: these codes also used as constraints
        //
        //               XXX         YYY         ZZZ         ISX       ISY       ISZ 
        //                                                   JSX       JSY       JSZ 
        //                                                   KSX       KSY       KSZ 
            0 SP   Object Space Reference Surface
                     0.000000     0.000000     0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            1 SP                                 
                    10.000000    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            2 SP                                 
                    12.000000    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            3 AS                                 
                    17.260000    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            4 SP                                 
                    17.260000    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            5 SP                                 
                    18.510000    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            6 SP                                 
                    23.200000    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            7 SP                                 
                    25.450000    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
            8 SP                                 
                    68.500828    -0.000000    -0.000000   1.000000  0.000000  0.000000
                                                          0.000000  1.000000  0.000000
                                                          0.000000  0.000000  1.000000
         <END>
        """

        command = 'disglocoo {} {}\n'.format(configurationNumber,referenceSurface)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()
        DisglocooOutput = self.RecvResponse(echo = self.echo)

        SurfaceList = []

        outputIter = iter(DisglocooOutput)
        for ThisLine in outputIter:
            ThisLine = ThisLine.strip()
            
            if not ThisLine:
                continue

            if ThisLine.startswith('//'):
                # Skip this one.
                continue

            if ThisLine.find('<END>') != -1:
                # Skip this one.
                continue
                
            # This is a real line of surface data.  Split on spaces.  The Glass
            # field may be empty.
            m = re.search('^(\d{1,5})\s(\w\w)\s?(.*)$', ThisLine)
            SurfaceNumber = int(m.group(1))
            TypeCode = m.group(2)
            Description = m.group(3).strip()
            
            if TypeCode in ['XD','XT','YD','YT','ZD','ZT']:
                # Parse the second line
                ThisLine = next(outputIter).strip()
                XXX, YYY, ZZZ = [float(token) for token in ThisLine.split()][:3]
                ThisSurfaceDict = {"SurfaceNumber"  : SurfaceNumber,
                                   "TypeCode"       : TypeCode,
                                   "XXX"            : XXX,
                                   "YYY"            : YYY,
                                   "ZZZ"            : ZZZ,
                                   }
                if len(ThisLine.split()) > 3:
                    for _ in range(2):
                        ThisLine = next(outputIter, None)
            else:
                # Parse the second line
                ThisLine = next(outputIter).strip()
                XXX, YYY, ZZZ, ISX, ISY, ISZ = [float(token) for token in ThisLine.split()]
                                                                
                # Parse the third line
                ThisLine = next(outputIter).strip()
                JSX, JSY, JSZ = [float(token) for token in ThisLine.split()]
            
                # Parse the fourth line
                ThisLine = next(outputIter).strip()
                KSX, KSY, KSZ = [float(token) for token in ThisLine.split()]

                ThisSurfaceDict = {"SurfaceNumber"  : SurfaceNumber,
                                   "TypeCode"       : TypeCode,
                                   "XXX"            : XXX,
                                   "YYY"            : YYY,
                                   "ZZZ"            : ZZZ,
                                   "ISX"            : ISX,
                                   "ISY"            : ISY,
                                   "ISZ"            : ISZ,
                                   "JSX"            : JSX,
                                   "JSY"            : JSY,
                                   "JSZ"            : JSZ,
                                   "KSX"            : KSX,
                                   "KSY"            : KSY,
                                   "KSZ"            : KSZ
                                  }

            SurfaceList.append(ThisSurfaceDict)

        return SurfaceList
        
    def GetRays(self,Wavelength,FieldPoints,PupilPoints):
        """ Return a set of traced rays from the Eikonal back end.

        The rays are returned as a list of lists of rays.

        """

        self.EikSubprocess.stdin.write(bytes("raytrasto {} {} {}\n".\
                format(Wavelength,FieldPoints,PupilPoints),'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(echo = self.echo)
        
        rayiter = iter(TextOutput)

        NewTextOutput = []
        
        #Clean the TextOutput and append to a new list
        for ThisLine in rayiter:
            ThisLine = ThisLine.strip()
            
            if not ThisLine:
                continue
            LineFields = ThisLine.split(',')
            if (LineFields[0].isdigit()):
                NewTextOutput.append(ThisLine)

        #Calculate length of new list
        lengthTextOutput = len(NewTextOutput)
        
        # Calculate number of surfaces
        NumSurfaces = self.GetNumSurfaces(0, skip=['XT','XD','YT','YD','ZT','ZD'])
        
        # Read the number of pupil points from the second to last line
        NumPupilPoints = int(NewTextOutput[lengthTextOutput - 1])
        
        #Calculate the number of rays
        NumRays = int((lengthTextOutput-2)/NumSurfaces)
        
        RayList = []
        
        for i in range(NumRays):

            ThisRay = []

            # Read the data for a single ray having NumSurfaces segments
            for j in range(NumSurfaces):


                #Read the data for a single ray segment

                ThisLine = NewTextOutput[1+i*(NumSurfaces)+j].strip()
                LineFields = ThisLine.split(',')

                ThisRaySegmentDict = {"SurfaceNumber"  : int(LineFields[0]),
                                      "XPos"           : float(LineFields[1]),
                                      "YPos"           : float(LineFields[2]),
                                      "ZPos"           : float(LineFields[3]),
                                      "RCosX"          : float(LineFields[4]),
                                      "RCosY"          : float(LineFields[5]),
                                      "RCosZ"          : float(LineFields[6]),
                                      "NCosX"          : float(LineFields[7]),
                                      "NCosY"          : float(LineFields[8]),
                                      "NCosZ"          : float(LineFields[9]),
                                      "n"              : float(LineFields[10]),
                                      "OpAngle"        : float(LineFields[11])
                                     }
                ThisRay.append(ThisRaySegmentDict)
            RayList.append(ThisRay)

        return RayList

    def InsSur(self,argsList):
        """ Insert spherical surface

        Example command for the back end:

        insrefracsur 0 3 3.4 2.0 3.0 4.0 BK7
        insreflecsur 0 3 3.4 2.0 3.0 4.0

        argsList will contain these parameters.

        """

        # Turn the list of strings into the Fortran-style space-delimited text,
        # leaving off the final argument, which is the 'type' ('reflective' or
        # 'refractive').

        argsString = '{}'.format(argsList[:-1]).strip('[]').replace('\'','').replace(',','')

        if argsList[-1] == 'reflective':

            commandname = 'INSREFLECSUR'

        elif argsList[-1] == 'refractive':

            commandname = 'INSREFRACSUR'

        else:

            return 'ERROR - surface type must be one of "reflective" or "refractive"'

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            # Currently, the back end provides no useful output from the
            # INSREF***SUR command.  The caller needs to look again at the
            # surfaces to make sure it was done as intended.

            return 'OK'

        return TextOutput

    def RemSur(self,argsList):
        """ Remove an existing surface

        Back end usage: REMSUR <c> <sn>
        where c is the configuration #, sn is the surface #
        """
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        command = 'REMSUR {}\n'.format(argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(self.echo)

        if TextOutput[0].strip().startswith('<ERROR>'):
            return 'ERROR'
        else:
            return 'OK'

    def InsZerSur(self,argsList):
        """ Insert surface described by Zernike polynomial coefficients.

        Example command for the back end:

        insrefraczersur 0 3 3.4 2.0 3.0 4.0 0.0  0.3  0.0  0.4  0.0  0.0  0.5  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0 BK7

        argsList will contain these

        or similar for insrefleczersur

        """

        # Turn the list of strings into the Fortran-style space-delimited text,
        # leaving off the final argument, which is the 'type' ('reflective' or
        # 'refractive').

        argsString = '{}'.format(argsList[:-1]).strip('[]').replace('\'','').replace(',','')

        if argsList[-1] == 'reflective':

            commandname = 'INSREFLECZERSUR'

        elif argsList[-1] == 'refractive':

            commandname = 'INSREFRACZERSUR'

        else:

            return 'ERROR - surface type must be one of "reflective" or "refractive"'

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            # Currently, the back end provides no useful output from the
            # INSREFRACZERSUR command.  The caller needs to look again at the
            # surfaces to make sure it was done as intended.

            return 'OK'

        return TextOutput

    def InsApeSto(self,argsList):
        """ Insert aperture stop

        Back end usage :

        insapesto <config #> <insert after surf #> <dist from prev> <dis to next>

        Input should be a list containing all these args 

        The last element of the list is a flag indicating whether function ParEntPup will be called.

        """   
        configNum = int(argsList[0])
        surfNum = int(argsList[1])
        dp = float(argsList[2])
        dn = float(argsList[3])
        setParEntPup = str(argsList[4]).lower() == "true"

        command = 'INSAPESTO {} {} {} {}\n'.format(configNum, surfNum, dp, dn)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):
            return 'ERROR'
        elif setParEntPup:
            # Set paraxial pupil position by specifying surface number
            ParEntPupOutput = self.ParEntPup([configNum, surfNum + 1])
            return ParEntPupOutput
        return 'OK'

    def ChaApeSto(self,argsList):
        """ Change an existing surface to an aperture stop or change position of aperture stop

        Example command for the back end:

        chaapesto <config #> <replace surf #> <dist from prev> <dis to next>

        Input should be a list containing all these args
        
        The last element of the list is a flag indicating whether function ParEntPup will be called.

        """
        configNum = int(argsList[0])
        surfNum = int(argsList[1])
        dp = float(argsList[2])
        dn = float(argsList[3])
        setParEntPup = str(argsList[4]).lower() == "true"

        command = 'CHAAPESTO {} {} {} {}\n'.format(configNum, surfNum, dp, dn)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):
            return 'ERROR'
        elif setParEntPup:
            # Set paraxial pupil position by specifying surface number
            ParEntPupOutput = self.ParEntPup([configNum, surfNum])
            return ParEntPupOutput
        return 'OK'

    def ParEntPup(self,argsList):
        """ Change paraxial entrance pupil position control

        Back end usage: PARENTPUP <configuration #> <FREE | TELECENTRIC | NC | surface #>
        
        """
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        command = 'PARENTPUP {}\n'.format(argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def ChaReflecSur(self,argsList):
        """ Change the parameters of an existing reflective surface

        Example command for the back end (see back end docs):

        charefracsur <config> <surf> <radius> <dist from prev> <dist to next>

        """

        # Turn the list of strings into the Fortran-style space-delimited text.

        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'CHAREFLECSUR'

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def ChaRefracSur(self,argsList):
        """ Change the parameters of an existing refractive surface

        Example command for the back end (see back end docs):

        charefracsur <config> <surf> <radius> <dist from prev> <dist to next> <glass>

        """

        # Turn the list of strings into the Fortran-style space-delimited text.

        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'CHAREFRACSUR'

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'
        
    def ChaRefereSur(self,argsList):
        """ Change the position/glass of the reference surface

        Back end usage:

        CHAREFERESUR <CONFIGURATION NUMBER> <DIST TO NEXT SURFACE> <GLASS NAME> [SURFACE DESC - 40 CHARS]

        """

        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        command = 'CHAREFERESUR {}\n'.format(argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(self.echo)

        if TextOutput[0].strip().startswith('<ERROR>'):
            return 'ERROR'
        else:
            return 'OK'

    def SurMov(self,argsList):
        """ Moves (displaces, decenters) one or more surfaces.

        Example command for the back end (see back end docs):

        SURMOV <c> <n> <d> <axis>

        """

        # Turn the list of strings into the Fortran-style space-delimited text.
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'SURMOV'

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(self.echo)

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def SurTil(self,argsList):
        """ Tilts (rotates) one or more surfaces.

        Example command for the back end (see back end docs):

        SURTIL <c> <n> <a> <p> <axis>

        """

        # Turn the list of strings into the Fortran-style space-delimited text.
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'SURTIL'

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(self.echo)

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def ChaZerSur(self,argsList):
        """ Change surface described by Zernike polynomial coefficients.

        Example command for the back end:

        charefraczersur 0 3 3.4 2.0 3.0 4.0 0.0  0.3  0.0  0.4  0.0  0.0  0.5  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0 BK7

        argsList will contain these

        or similar for charefleczersur

        """

        # Turn the list of strings into the Fortran-style space-delimited text,
        # leaving off the final argument, which is the 'type' ('reflective' or
        # 'refractive').

        argsString = '{}'.format(argsList[:-1]).strip('[]').replace('\'','').replace(',','')

        if argsList[-1] == 'reflective':

            commandname = 'CHAREFLECZERSUR'

        elif argsList[-1] == 'refractive':

            commandname = 'CHAREFRACZERSUR'

        else:

            return 'ERROR - surface type must be one of "reflective" or "refractive"'

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            # Currently, the back end provides no useful output from the
            # CHAREFRACZERSUR command.  The caller needs to look again at the
            # surfaces to make sure it was done as intended.

            return 'OK'

        return TextOutput

    def GetSurfaceDataTable(self,argsList):
        """ Return or save a text table of surface data

        Example command for the back end (see back end docs):

        dansysdat8 (to write to stdout)
        dansysdat9 (to write to systemdata.dat file)

        argsList is ['return'] or ['save'] for dansysdat8 and dansysdat9,
        respectively.

        """

        try:
            destination = argsList[0]
        except:
            return 'ERROR - missing arguments'

        if not destination in ['return','save']:
            return 'ERROR - invalid arguments'

        # Turn the list of strings into the Fortran-style space-delimited text.

        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'DANSYSDAT{}'.format({'return':'8','save':'9'}[destination])

        command = '{} {}\n'.format(commandname,argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        elif destination == 'save':

            return 'OK - wrote systemdata.dat'

        else:

            # Convert the list of string output to a single string delimited
            # with line breaks, leaving off "<END>".

            return ''.join(TextOutput[:-2])

    def Eval(self,argslist=[]):
        """ Quick implementation of $eval command

        This needs no arguments.

        """


        self.EikSubprocess.stdin.write(bytes('$eval\n','ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(echo=self.echo)

        return None

    def SlideAndRayTrace(self,argsList):
        """ Adjust position of surfaces, return rays for each position

        This can be used to generate a set of ray trace data for a range of
        positions of a lens along the optical axis.

        It moves a pair of surfaces together, using CHAREFRACSUR or
        CHAREFLECSUR and does a RAYTRA at each position.  This requires two
        CHAREF*SURs and one RAYTRA for each position.

        NOTE: The surfaces are moved back to their original positions after
        doing the ray-tracing.  The purpose is to precalculate ray trace data,
        not to alter the system.

        The full set of ray trace data vs. position is returned in one batch to
        reduce the effect of network latency.  Currently, the data are returned
        as text.

        Args expected (in order):

            configNum          <int> configuration number of the system,
            firstSurf          <int> first surface to be moved,
            lastSurf           <int> last surface to be moved,
            rangeOfMov         <float> distance a surface can move
            numberOfPositions  <int> how many equal divisions of the position 
                                of the surfaces to trace rays for,
            QFN                <float> equivalent f/# to set after each move of the lenses

        """

        # charefracsur <config> <surf> <radius> <dist from prev> <dist to next> <glass>
        # self.ChaRefracSur(...

        configNum    = int(argsList[0])
        firstSurf    = int(argsList[1])
        lastSurf     = int(argsList[2])
        rangeOfMov   = float(argsList[3])
        numOfPos     = int(argsList[4])
        QFN          = float(argsList[5])



        # Need to get the distance from the first surface to the second so that
        # we can hold it constant as we move the requested parts of the lens.
        # Need radius so that we can keep it constant also.

        originalSurfaces          = self.GetSurfaces(configNum)
        distToNext                = originalSurfaces[firstSurf]['DistToNext']
        curvatureFirstSurf        = originalSurfaces[firstSurf]['Curvature']
        if curvatureFirstSurf !=0: 
            radiusFisrtSurf           = 1.0 / curvatureFirstSurf
        else:
            radiusFisrtSurf           = 1.0 /0.000000001    
        distFromPrevious          = originalSurfaces[lastSurf - 1]['DistToNext']
        curvatureLastSurf         = originalSurfaces[lastSurf]['Curvature']
        if curvatureLastSurf !=0:
            radiusLastSurf            = 1.0 / curvatureLastSurf
        else:
            radiusLastSurf           = 1.0 /0.000000001             
        initialDistanceFromPrev   = originalSurfaces[firstSurf - 1]['DistToNext']
        initialDistanceToNext     = originalSurfaces[lastSurf]['DistToNext']

        # The surface may or may not have a glass code.

        if 'GlassCode' in originalSurfaces[firstSurf].keys():
            glassFirstSurf = originalSurfaces[firstSurf]['GlassCode']
        else:
            glassFirstSurf = None

        if 'GlassCode' in originalSurfaces[lastSurf].keys():
            glassLastSurf = originalSurfaces[lastSurf]['GlassCode']
        else:
            glassLastSurf = None


        
        # The set of positions to calculate rays for (from firstSurf to its
        # previous surface).

        positions = np.linspace(0.0,rangeOfMov,numOfPos)

        # A dict that maps positions of the first surface to the set of rays
        # traced for that position.

        raysForPositions = {}

        # A list to return the positions corresponding to the sets of ray data:

        systemPositions  = []

        # Loop over these positions, setting f/# etc. and tracing rays at each
        # position.

        for pos in positions:
            posLastSurface    = rangeOfMov - pos
            if firstSurf != 0:
                if firstSurf != lastSurf:                  
                    argsListFirstSurf = [configNum,str(firstSurf),str(radiusFisrtSurf), str(pos), distToNext]
                    argsListLastSurf  = [configNum,str(lastSurf),str(radiusLastSurf), distFromPrevious, str(posLastSurface)]

                    if not glassFirstSurf == None:
                        argsListFirstSurf.append(glassFirstSurf)

                    if not glassLastSurf == None:
                        argsListLastSurf.append(glassLastSurf)
                
                    self.ChaRefracSur(argsListFirstSurf)
                    self.ChaRefracSur(argsListLastSurf)
                else:
                    argsListFirstSurf = [configNum,str(firstSurf),str(radiusFisrtSurf), str(pos), str(posLastSurface)]                    

                    if not glassFirstSurf == None:
                        argsListFirstSurf.append(glassFirstSurf)

                    self.ChaRefracSur(argsListFirstSurf)
            else:
                if firstSurf != lastSurf:                  
                    argsListFirstSurf = [configNum, distToNext]
                    argsListLastSurf  = [configNum,str(lastSurf),str(radiusLastSurf), distFromPrevious, str(posLastSurface)]

                    if glassFirstSurf == 0.0:
                        argsListFirstSurf.append('air')

                    if not glassLastSurf == None:
                        argsListLastSurf.append(glassLastSurf)

                    
                    self.ChaRefereSur(argsListFirstSurf)
                    self.ChaRefracSur(argsListLastSurf)
                else:
                    argsListFirstSurf = [configNum,str(posLastSurface)]                    

                    if glassFirstSurf == 0.0:
                        argsListFirstSurf.append('air')

                    self.ChaRefereSur(argsListFirstSurf)

            # Reset the QFN value (because it changes when you move a surface).
            self.SetParameter(['QFN', 'M', str(QFN)])

            # Run $eval.
            self.Eval()

            # Run raytra (0 2 3 for now)
            rayList = self.GetRays(0,2,3)

            # Add ray data to the set to be returned.
            raysForPositions[pos] = rayList

            # Get the lens positions for that set of rays so that the caller
            # can cross-check.
            systemPositions.append(self.GetSurfaces(0))

        if firstSurf != 0:
            argsListFirstSurf = [configNum,str(firstSurf),str(radiusFisrtSurf), initialDistanceFromPrev, distToNext]
            argsListLastSurf  = [configNum,str(lastSurf),str(radiusLastSurf), distFromPrevious, initialDistanceToNext]
            if not glassFirstSurf == None:
                argsListFirstSurf.append(glassFirstSurf)

            if not glassLastSurf == None:
                argsListLastSurf.append(glassLastSurf)


            self.ChaRefracSur(argsListFirstSurf)
            self.ChaRefracSur(argsListLastSurf)
        else:
                if firstSurf != lastSurf:                  
                    argsListFirstSurf = [configNum, distToNext]
                    argsListLastSurf  = [configNum,str(lastSurf),str(radiusLastSurf), distFromPrevious, initialDistanceToNext]

                    if glassFirstSurf == 0.0:
                        argsListFirstSurf.append('air')

                    if not glassLastSurf == None:
                        argsListLastSurf.append(glassLastSurf)

                    
                    self.ChaRefereSur(argsListFirstSurf)
                    self.ChaRefracSur(argsListLastSurf)
                else:
                    argsListFirstSurf = [configNum,initialDistanceToNext]                    

                    if glassFirstSurf == 0.0:
                        argsListFirstSurf.append('air')

                    print(argsListFirstSurf)
                    self.ChaRefereSur(argsListFirstSurf)            

        # Reset the QFN value (because it changes when you move a surface).
        self.SetParameter(['QFN', 'M', str(QFN)])

        # Run $eval.
        self.Eval()

        self.GetSurfaces(configNum)

        return raysForPositions, systemPositions

    def SetParameter(self, argsList=[]):
        """ Quick implementation of SET command 
        Backend Usage:
        SET <parameter name> <'M' or 'E'> <value>
        
        Input:
            argList:[parameter name, 'M' or 'E', value]
        """
        # Turn the list of strings into the Fortran-style space-delimited text.
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        command = 'SET {}\n'.format(argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'
        
        else:

            return 'OK' 

    def InsertFieldPoint(self, argsList=[]):
        """Quick implementation of INSFIEPOI command
        
        Back end usage:
        INSFIEPOI <"FIH" or "HFOV"> <configuration #> <y-value> <z-value>
        Input:
            argsList: [field type, configuration #, y value, z value]

        """

        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'INSFIEPOI'

        command = '{} {}\n'.format(commandname, argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def RemoveFieldPoint(self, argsList=[]):
        """ Quick implementation if REMFIEPOI command
        
        Back end Usage: REMFIEPOI <c> <fn>
        Input:
            argList:[configuration#, field#]
        """

        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'REMFIEPOI'

        command = '{} {}\n'.format(commandname, argsString)
        
        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'
            
        else:

            return 'OK'

    def ListFieldPoints(self, ConfigurationNumber):
        """ Return the list of fractional image heights of field points
            Returns:
                FieldPointList: [(f0_y_height, f0_z_height), ...]
            This function needs updates to parse Pupil Shift Coeff. and Pupil Expasion Coeff
        
        """

        command = 'LISFIEPOI {}\n'.format(ConfigurationNumber)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        LisfiepoiOutput = self.RecvResponse()

        FieldPointList = []

        for i in range(len(LisfiepoiOutput)):

            ThisLine = LisfiepoiOutput[i].strip()
            
            if ThisLine.startswith('fld.'):
                #read first line
                LineFields = ThisLine.split()
                FieldPointList.append((float(LineFields[3]),float(LineFields[4])))
        
        return FieldPointList

    def SetImageDistanceSolve(self, argsList=[]):
        """ Quick implementation of SETIMADISSOL command
        
        Example command for the back end (see back end docs):
        SETIMADISSOL <configuration #> <'yes' or 'no'>

        Input:
            argList: [configuration #, 'yes' or 'no']
        """
        # Turn the list of strings into the Fortran-style space-delimited text.
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'SETIMADISSOL'

        command = '{} {}\n'.format(commandname,argsString)
        
        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'
    
    def SetRotSym(self, argsList=[]):
        """ Quick implementation of SETROTSYM command

        back end usage:

        SETROTSYM <configuration #> <symmetry code>

        """
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        command = 'SETROTSYM {}\n'.format(argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def SetAbeSym(self, argsList=[]):
        """ Quick implementation of SETABESYM command

        back end usage:

        SETABEYM <configuration #> <symmetry code>
        
        """
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        command = 'SETABESYM {}\n'.format(argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def ChaSysCla(self, argsList=[]):
        """ change the system class for the optical system

        Back end usage:

        CHASYSCLA <CONFIGURATION NUMBER> [M|E] [OBJ|CRL|ARL|TEL|EYP|AUF|AUI]

        """
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        command = 'ChaSysCla {}\n'.format(argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'

        else:

            return 'OK'

    def GetGenSysSet(self, ConfigurationNumber):
        """ Get the general system settings

        back end usage: GETGENSYSSET <configuration #>

        return a dict of system settings for current configuration

        """
        ImaDisSol = enum.Enum('ImaDisSol',{'On':True,'Off':False})
        SysTyp = enum.Enum('SysTyp','Objective CommonRelay AfocalRelay Telescope Eyepiece\
            AutoCollimatorFinite AutoCollimatorInfinite')
        RotSym = enum.Enum('RotSym', 'RotationallySymmetric Anamorphic')
        AbeSym = enum.Enum('AbeSym', 'Symmetric Asymmetric')
        PupSha = enum.Enum('PupSha', 'CircularOrElliptical SqureOrRectangular')
        SysSet = enum.Enum('SysSet', 'Collinear NoncollinearExplicit NoncollinearImplicit')
        CooSys = enum.Enum('CooSys', 'Standard Canonical')
        
        command = 'GETGENSYSSET {}\n'.format(ConfigurationNumber)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        GensyssetOutput = self.RecvResponse()

        if  GensyssetOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'
        
        outputIter = iter(GensyssetOutput)
        outputDict = {}

        for ThisLine in outputIter:
            ThisLine = ThisLine.strip()
            
            if not ThisLine:
                continue

            if ThisLine.find('<End>') != -1:
                continue

            if ThisLine.startswith('CURRENT'): 
                #skip "CURRENT HEADING STATUS:"
                continue
            
            if ThisLine.endswith(('(meridional)','(equatorial)')):
                plane = re.split('\(|\)',ThisLine)[-2][0].upper()
                key = 'SystemType ({})'.format(plane)
                if ThisLine.startswith('Obj'):
                    outputDict[key] = SysTyp(1).name
                elif ThisLine.startswith('Com'):
                    outputDict[key] = SysTyp(2).name
                elif ThisLine.startswith('Afo'):
                    outputDict[key] = SysTyp(3).name
                elif ThisLine.startswith('Tel'):
                    outputDict[key] = SysTyp(4).name
                elif ThisLine.startswith('Eye'):
                    outputDict[key] = SysTyp(5).name
                elif ThisLine.find('(finite)') != -1:
                    outputDict[key] = SysTyp(6).name
                else :
                    outputDict[key] = SysTyp(7).name
            elif ThisLine.endswith('ON'):
                outputDict['ImageDistanceSol'] = ImaDisSol(True).name
            elif ThisLine.endswith('OFF'):
                outputDict['ImageDistanceSol'] = ImaDisSol(False).name
            elif ThisLine.startswith('Rotational'):
                outputDict['RotationalSym'] = RotSym(1).name
            elif ThisLine.startswith('Anamorphic'):
                outputDict['RotationalSym'] = RotSym(2).name
            elif ThisLine.startswith('Symmetric'):
                outputDict['AberrationSym'] = AbeSym(1).name
            elif ThisLine.startswith('Asymmetric'):
                outputDict['AberrationSym'] = AbeSym(2).name
            elif ThisLine.startswith('Circular'):
                outputDict['PupilShape'] = PupSha(1).name
            elif ThisLine.startswith('Square'):
                outputDict['PupilShape'] = PupSha(2).name
            elif ThisLine.startswith('Strictly'):
                outputDict['SystemSetup'] = SysSet(1).name
            elif ThisLine.endswith('dummy sfces)'):
                outputDict['SystemSetup'] = SysSet(2).name
            elif ThisLine.endswith('hidden sfces)'):
                outputDict['SystemSetup'] = SysSet(3).name
            elif ThisLine.startswith('Standard'):
                outputDict['CoordinateSys'] = CooSys(1).name
            elif ThisLine.startswith('Canonical'):
                outputDict['CoordinateSys'] = CooSys(2).name

        return outputDict

    def GetFirstOrderParameter(self, argsList = []):
        """
        Backend Usage: get firordpar [configuration#] [M or E] [parameter name] 
        
        """
        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        commandname = 'GET FIRORDPAR'

        command = '{} {}\n'.format(commandname, argsString)

        self.EikSubprocess.stdin.write(bytes(command,'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse()

        FirstLine = TextOutput[0].strip()

        if FirstLine.startswith('<ERROR>'):

            return 'ERROR'

        else:
            LineFields = FirstLine.split(">")

            try:
                ParameterValue = float(LineFields[1])
            except:
                ParameterValue = LineFields[1].strip()

                if ParameterValue.startswith("-"): ### remove dash before the unit: <VAL UNI> -mm

                    return ParameterValue[1:]

                elif ParameterValue.startswith("***"):

                    return None

            return ParameterValue

    def GetWavelengths(self,ConfigurationNumber):
        """ Return the wavelengths of system

            The output is a list containing 3 wavelengths

            Back-end usage: GETWAVLEN <config #>

        """
        self.EikSubprocess.stdin.write(bytes("getwavlen {} \n".format(ConfigurationNumber),'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(echo=self.echo)

        if TextOutput[0].strip().startswith(('<ERROR>', '***')):

            return 'ERROR'

        else:

            wavelengths= list(map(float, TextOutput[0].strip().split()))
            
            return wavelengths

    def SetWavelengths(self, argsList):
        """ Set the three wavelengths of the system

        Back-end usage : <CONFIGURATION NUMBER> <BASIC> <SHORT> <LONG> [R|C]

        """

        argsString = '{}'.format(argsList).strip('[]').replace('\'','').replace(',','')

        self.EikSubprocess.stdin.write(bytes("setwavlen {} \n".format(argsString),'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(echo=self.echo)

        if TextOutput[0].strip().startswith('<ERROR>'):

            return 'ERROR'
            
        else:

            return 'OK'
            
    def SaveSystem(self,FileName,overWrite):
        """ Saves a system .A file in the Eikonal back end.

        back end Usage: SAVSYS <FILE-PATH>
        """

        basename = os.path.splitext(FileName)[0]

        if os.path.exists("{}.A".format(basename)) and str(overWrite).lower() == "true":
            print(" <OVERWRITING> {}.A ".format(basename))
            os.remove("{}.A".format(basename))

        self.EikSubprocess.stdin.write(bytes("savsys '{}' \n".format(basename),'ascii'))
        self.EikSubprocess.stdin.flush()

        TextOutput = self.RecvResponse(echo=self.echo)

        if TextOutput[0].strip().startswith('<ERROR>'):
            return 'ERROR'
        else:
            return 'OK'

if __name__ == '__main__':



    core = Core()

    #core.LoadSystem("550401.DBS")
    #
    #print "Getting Surface list"
    #surfaces = core.GetSurfaces(ConfigurationNumber=0)
    #
    #print "Surface 1:"
    #for one in surfaces[0]:
    #    print one, surfaces[0][one]
    #
    #print "Getting Ray list"
    #rays=core.GetRays(1,0,3)
    #
    #print "Ray 1:"
    #for segment in rays[0]:
    #    for one in segment:
    #        print one, segment[one]
    #
    #
    #core.EikSubprocess.stdin.write("x\n")
    #core.EikSubprocess.stdin.flush()