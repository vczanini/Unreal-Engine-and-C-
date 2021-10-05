#!/usr/bin/python

import Config
import Core
import GetPaths
import json
import time
import zmq
import platform
from ParseSeq import SeqObject
if (platform.system() == "Windows"):
    from GetFFDData import FFD

class Interface(object):

    defaultServerIP   = 'localhost'
    defaultServerPort = 5556

    def __init__(self,PrintDebugInfo):

        self.PrintDebugInfo = PrintDebugInfo

        self.Paths = GetPaths.GetPaths()

        self.Configurator = Config.Config(FilePath = self.Paths.Get("CONFIG_FILEPATH"))

        try:
            self.serverIP = self.Configurator.Get('Server','ServerIP')
        except:
            self.serverIP = self.defaultServerIP

        try:
            self.serverPort = self.Configurator.Get('Server','ServerPort')
        except:
            self.serverPort = self.defaultServerPort

        self.context= zmq.Context();
        #  Socket to talk to server
        if self.PrintDebugInfo:
            print("Connecting to server")

        self.socket = self.context.socket(zmq.REQ)

        serverString = 'tcp://{}:{}'.format(self.serverIP,self.serverPort)
        self.socket.connect(serverString)

        if (platform.system() == "Windows"):
            self.Codev = FFD()
            if (self.Codev.CodeVFlag == False):
                self.Codev.StartCodev()


    def Stop(self):

        if self.PrintDebugInfo:
            print('Sending request "Stop"' )
        self.socket.send_string("Stop")

        if (platform.system() == "Windows"):
            if (self.Codev.CodeVFlag == True):
                self.Codev.StopCodev()


    def SetCoreEcho(self,args):
        """ Tell the Core to turn echo on or off

        """

        echo = args['echo']

        if echo:
            message = 'SetEcho on'
        else:
            message = 'SetEcho off'

        self.socket.send_string(message)
        return self.socket.recv_pyobj()

    def Command(self,message):
        """ General purpose low-level command and response

        This talks to the Core and returns text or python objects.

        """

        if self.PrintDebugInfo:
            print(('Sending request "%s"' % message))
        self.socket.send_string(message)

        return self.socket.recv_pyobj()

    def SpeedTest(self,args):
        """ Talk to the Core repeatedly and return the average round-trip time.

        """

        iterations  = args['iterations']
        messageSize = args['messageSize']

        message = 'SpeedTest ' + (messageSize - 10) * 'x'

        startTime = time.time()

        for i in range(iterations):

            self.socket.send_string(message)
            response = self.socket.recv_pyobj()
            assert response == message

        totalTime   = time.time() - startTime
        averageTime = 1000.0 * totalTime / (i + 1) # ms

        return averageTime

    def LoadSystem(self,FileName):
        """ Loads a .A system file

        """

        if self.PrintDebugInfo:
            print('Sending request "LoadSystem"')

        self.socket.send_string("%s %s" % ("LoadSystem", FileName))

        # Get the reply if system loaded successfully
        reply = self.socket.recv_pyobj()
        if self.PrintDebugInfo:
            print(reply)

        return None

    def GetNumSurfaces(self,ConfigurationNumber):
        """ Return an integer number of surfaces

        """

        if self.PrintDebugInfo:
            print('Sending request "GetNumSurfaces"' )

        self.socket.send_string("%s %d" % ("GetNumSurfaces", ConfigurationNumber))
        #  Get the reply.
        NumSurfaces = self.socket.recv_pyobj()


        return NumSurfaces

    def GetSurfaces(self,ConfigurationNumber):
        """ Return a list of dicts, one dict per surface.

        """

        if self.PrintDebugInfo:
            print('Sending request "GetSurfaces"' )

        self.socket.send_string("%s %d" % ("GetSurfaces", ConfigurationNumber))
        #  Get the reply.
        Surfaces = self.socket.recv_pyobj()

        return Surfaces

    def GetSurfacesGlobal(self,args):
        """ Return a list of dicts using global coordinates

        Compare to GetSurfaces.

        """

        ConfigurationNumber = args['c']
        ReferenceSurface    = args['rs']

        if self.PrintDebugInfo:
            print('Sending request "GetSurfacesGlobal"' )

        self.socket.send_string("%s %d %d" % ("GetSurfacesGlobal",ConfigurationNumber,ReferenceSurface))
        Surfaces = self.socket.recv_pyobj()

        return Surfaces

    def GetSurfaceDataTable(self,destination='return'):
        """ Return or save a text table of surface data

        destination is one of 'return' or 'save'.

        """
        allowedDests = ['return','save']

        if not destination in allowedDests:
            raise ValueError('destination must be one of {}'.format(allowedDests))

        if self.PrintDebugInfo:
            print('Sending request "GetSurfaceDataTable"' )

        self.socket.send_string('{} {}'.format("GetSurfaceDataTable", destination))
        response = self.socket.recv_pyobj()

        if destination == 'save':

            return {'ERROR':False,'OK':True}[response]

        else:

            return response

    def GetRays(self,Wavelength,FieldPoints,PupilPoints):
        """ Return a list of rays, each ray being a list of dictionaries, one dict per ray segment

        """

        if self.PrintDebugInfo:
            print('Sending request "GetRays"' )

        self.socket.send_string("%s %d %d %d" % ("GetRays", Wavelength, FieldPoints, PupilPoints))

        #  Get the reply.
        Rays = self.socket.recv_pyobj()

        return Rays

    def ChangeReflectiveSurface(self,args):
        """ Change position or other parameters of reflective surface

        """

        if self.PrintDebugInfo:
            print('Sending request "ChaReflecSur"')

        command = 'ChaReflecSur {} {} {} {} {}'.format(
                                                       args['c'],  # config
                                                       args['s'],  # surface
                                                       args['r'],  # new radius
                                                       args['dp'], # new dist from prev
                                                       args['dn'], # new dist to next
                                                      )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def ChangeRefractiveSurface(self,args):
        """ Change position or other parameters of refractive surface

        """

        if self.PrintDebugInfo:
            print('Sending request "ChaRefracSur"')

        command = 'ChaRefracSur {} {} {} {} {} {}'.format(
                                                       args['c'],  # config
                                                       args['s'],  # surface
                                                       args['r'],  # new radius
                                                       args['dp'], # new dist from prev
                                                       args['dn'], # new dist to next
                                                       args['gl'], # new glass
                                                      )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def InsertSurface(self,args):
        """ Insert a spherical surface

        NOTE:  $EVAL should be run after this.

        *Back end* usage:

            INSREFRACSUR <c> <p> <r> <dp> <dn> <g>
            (similar for reflective)

        where c is the configuration number (starting from 0),
        s is the index of the surface after which to insert this surface (starting from 0),
        r is the radius of curvature to first order
        dp is the distance from the previous surface (surface p),
        dn is the distance to the next surface,
        gl is the glass code from the catalog (8 characters max, e.g. "BK7", and

        args is a dict containing the arguments above:

        {
         'c'     : 0,
         's'     : 3,
         'r'     : 3.4,
         'dp'    : 2.0,
         'dn'    : 3.0,
         'gl'    : 'BK7',
         'type'  : 'reflective',
        }

        type is one of 'reflective' and 'refractive'

        Returns True for success, False for error.

        """

        if self.PrintDebugInfo:
            print('Sending request "InsSur"')

        if args['type'] == 'reflective':
            gl = ''
        else:
            gl = args['gl']

        command = 'InsSur {} {} {} {} {} {} {}'.format(
                                                                args['c'],
                                                                args['s'],
                                                                args['r'],
                                                                args['dp'],
                                                                args['dn'],
                                                                gl,
                                                                args['type']
                                                               )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def InsertZernike(self,args):
        """ Insert a zernike surface

        NOTE:  $EVAL should be run after INSREFRACZERSUR.

        *Back end* usage:

            INSREFRACZERSUR <c> <p> <r> <dp> <dn> <su> <a1 , a2 , ..., a35 > <g> [title]

        where c is the configuration number (starting from 0),
        p is the index of the surface after which to insert this surface (starting from 0),
        r is the radius of curvature to first order (the sperical term),
        dp is the distance from the previous surface (surface p),
        dn is the distance to the next surface,
        su is the radius over which the Zernike polynomials are defined
        a1, a2 , ..., a35 are the coefficients of the Zernike polynomial,
        g is the glass code from the catalog (8 characters max, e.g. "BK7", and

        args is a dict containing the arguments above:

        {
         'c'     : 0,
         'p'     : 3,
         'r'     : 3.4,
         'dp'    : 2.0,
         'dn'    : 3.0,
         'su'    : 4.0,
         'an'    : [0.0,0.3,0.0,0.4,0.0,0.0,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],
         'b'     : 'BK7',
         'type'  : 'reflective',
        }

        type is one of 'reflective' and 'refractive'

        Returns True for success, False for error.

        """

        if self.PrintDebugInfo:
            print('Sending request "InsZerSur"')

        anStr = str(args['an']).strip('[]').replace(',',' ')

        command = 'InsZerSur {} {} {} {} {} {} {} {} {}'.format(
                                                                args['c'],
                                                                args['p'],
                                                                args['r'],
                                                                args['dp'],
                                                                args['dn'],
                                                                args['su'],
                                                                anStr,
                                                                args['b'],
                                                                args['type']
                                                               )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def InsertApertureStop(self, args, setParEntPup=True):
        """ Insert an aperure stop

        NOTE:  $EVAL should be run after this.

        *Back end* usage:
            INSAPESTO <c> <p> <dp> <dn>
        where c is the configuration number (starting from 0),
        s is the index of the surface after which to insert aperture stop (starting from 0),
        dp is the distance from the previous surface (surface p),
        dn is the distance to the next surface,

        args is a dict containing the arguments above:
        {
         'c'     : 0,
         's'     : 3,
         'dp'    : 2.0,
         'dn'    : 3.0
        }

        setParEntPup should be False if paraxial Entrance pupil control is not needed
        """      
        if self.PrintDebugInfo:
            print('Sending request "InsApeSto"')

        command = 'InsApeSto {} {} {} {} {}'.format(
                                                args['c'],
                                                args['s'],
                                                args['dp'],
                                                args['dn'],
                                                setParEntPup,
                                                )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
    
    def ChangeApertureStop(self,args,setParEntPup=True):
        """ Change position of aperture stop or change an existing surface to apeture stop

        *Back end* usage:
            INSAPESTO <c> <p> <dp> <dn>
            
        where c is the configuration number (starting from 0),
        s is the index of the surface of the aperture stop,
        dp is the distance from the previous surface (surface p),
        dn is the distance to the next surface,

        args is a dict containing the arguments above:
        {
         'c'     : 0,
         's'     : 3,
         'dp'    : 2.0,
         'dn'    : 3.0
        }
        """
        if self.PrintDebugInfo:
            print('Sending request "ChaApeSto"')

        command = 'ChaApeSto {} {} {} {} {}'.format(
                                                args['c'],
                                                args['s'],
                                                args['dp'],
                                                args['dn'],
                                                setParEntPup,
                                                )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
    
    def ChangeZernike(self,args):
        """ Change position or other parameters of zernike surface

        """

        if self.PrintDebugInfo:
            print('Sending request "ChaZerSur"')

        # Split coefficients into space-delimited
        coeffs = str(args['an']).strip('[]').replace(',',' ')

        # See if there's a glass (refractive) defined.
        if 'b' in args:
            glass = args['b']
        else:
            glass = ' '

        command = 'ChaZerSur {} {} {} {} {} {} {} {} {}'.format(
                                                       args['c'],  # config
                                                       args['p'],  # surface
                                                       args['r'],  # new radius
                                                       args['dp'], # new dist from prev
                                                       args['dn'], # new dist to next
                                                       args['su'], # new surface radius
                                                       coeffs,     # Zernike expansion coefficients
                                                       glass,      # new glass
                                                       args['type'] # Refractive or reflective
                                                      )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def RemoveSurface(self,ConfigurationNumber,SurfaceNumber):
        """ Remove a surface

        """
        if self.PrintDebugInfo:
            print('Sending request "RemSur"')

        command = 'RemSur {} {}'.format(ConfigurationNumber,SurfaceNumber)

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
            
    def ChangeReferenceSurface(self,args):
        """ Change position or glass of reference surface

        back end usage: CHAREFERESUR <c> <dn> <gl>

        where c is the configuration #,
        dn is the distance to the next surface,
        g is the glass code from the catalog.

        args is a dict containing the arguments above: {'c': 0, 'dn': 2.0, 'gl': 'AIR' }
        
        """
        if self.PrintDebugInfo:
            print('Sending request "ChaRefereSur"')

        command = 'ChaRefereSur {} {} {}'.format(
                                            args['c'],
                                            args['dn'],
                                            args['gl'],
                                            )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SlideAndRayTrace(self,args):
        """ Call Core to adjust position of surfaces, return rays for each position

        This can be used to generate a set of ray trace data for a range of
        positions of a lens along the optical axis, all at once, to allow for
        fast animation in the UI.

        The full set of ray trace data vs. position is returned in one batch to
        reduce the effect of network latency.  Currently, the data are returned
        as text.

        The ray traces for positions will be returned as

        {pos1:[[{ray point},{ray point}...],[another ray],...],pos2:[...]}

        where each list is the usual ray tracing format.

        This function is called by SlideAndRayTrace(args), where args is

           { 
            configNum          <int> configuration number of the system,
            firstSurf          <int> first surface to be moved,
            lastSurf           <int> last surface to be moved,
            rangeOfMov         <float> distance a surface can move
            numberOfPositions  <int> how many equal divisions of the position 
                                of the surfaces to trace rays for,
            QFN                <float> equivalent f/# to set after each move of the lenses
            }

        """

        command = 'SlideAndRayTrace {} {} {} {} {} {}'.format(
                                                           args['configNum'],
                                                           args['firstSurf'],
                                                           args['lastSurf'],
                                                           args['rangeOfMov'],
                                                           args['numberOfPositions'],
                                                           args['QFN'],
                                                          )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        rays, positions = response

        # Testing a format for the returned data that converts the rays and
        # positions (lissur output) into string format separated by '$'.

        stringResponse = json.dumps(rays) + '$' + json.dumps(positions)

        # return response
        return stringResponse

    def SurfaceMove(self,args):
        """ Moves (displaces, decenters) one or more surfaces.

        NOTE:  $EVAL should be run after SURMOV.

        *Back end* usage:

            SURMOV <c> <n> <d> <axis>

        where c is the configuration number (starting from 0),
        n is the index of the surface to move,
        d is the distance in system units,
        axis is one of “x,” “y,” or “z,” the pivot axis.
        
        args is a dict containing the arguments above:

        {
         'c'     : 0,
         'n'     : 1,
         'd'     : 0.2,
         'axis'  : 'y',
        }

        Returns True for success, False for error.

        """

        if self.PrintDebugInfo:
            print('Sending request "SurMov"')

        command = 'SurMov {} {} {} {}'.format(
                                            args['c'],
                                            args['n'],
                                            args['d'],
                                            args['axis'],
                                            )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
            
    def SurfaceTilt(self,args):
        """ Tilts (rotates) one or more surfaces.

        NOTE:  $EVAL should be run after SURMOV.

        *Back end* usage:

            SURTIL <c> <n> <a> <p> <axis>

        where c is the configuration number (starting from 0),
        n is the index of the surface to tilt,
        a is the tilt angle in degrees,
        p is the distance from surface n to the pivot axis and
        axis is one of “x,” “y,” or “z,” the pivot axis.
        
        args is a dict containing the arguments above:

        {
         'c'     : 0,
         'n'     : 1,
         'a'     : -15,
         'p'     : 0,
         'axis'  : 'y',
        }

        Returns True for success, False for error.

        """

        if self.PrintDebugInfo:
            print('Sending request "SurTil"')

        command = 'SurTil {} {} {} {} {}'.format(
                                            args['c'],
                                            args['n'],
                                            args['a'],
                                            args['p'],
                                            args['axis'],
                                            )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
    def MoveAndReturn(self, args):
        """ This function moves one surface and optical axis should return to
        
        the original "X" direction after moving the surface.
        
        args is a dict containing the arguments below:

        {
         'c'          : 0,
         'surfNum     : 1,
         'axis'       : 'y',
         'dist'       : '10',
        },

        where: 
            'c' is the configuration number
            'surfNum' is the index of the surface to be tilted
            'axis' is the the pivot axis. Should be one of "x" "y" or "z"
            'dist' is the distance to move, in system unit

        Returns True for success, False for error.

        """

        configuration = args['c']
        surfNum       = args['surfNum']
        axis          = args['axis']
        distance        = args['dist']

        origianlSurfaces = self.GetSurfaces(configuration)

        response = self.SurfaceMove({'c': configuration,
                                     'n': surfNum - 1,
                                     'd': distance,
                                     'axis': axis})
        if not response:
            return False
        
        response = self.SurfaceMove({'c': configuration,
                                     'n': surfNum + 1,
                                     'd': -distance,
                                     'axis': axis})

        if not response:
            return False

        return True

    def MoveAndBend(self, args):
        """ this function moves one surface and moves the optical axis

        in the same direction by twice the distance
        
        args is a dict containing the arguments below:

        {
         'c'          : 0,
         'surfNum     : 1,
         'axis'       : 'y',
         'dist'       : '10',
        },

        where: 
            'c' is the configuration number
            'surfNum' is the index of the surface to be tilted
            'axis' is the the pivot axis. Should be one of "x" "y" or "z"
            'dist' is the distance to move the surface, in system unit

        Returns True for success, False for error.
        """

        configuration = args['c']
        surfNum       = args['surfNum']
        axis          = args['axis']
        distance      = args['dist']

        origianlSurfaces = self.GetSurfaces(configuration)

        response = self.SurfaceMove({'c': configuration,
                                     'n': surfNum - 1,
                                     'd': distance,
                                     'axis': axis})
        if not response:
            return False
        
        response = self.SurfaceMove({'c': configuration,
                                     'n': surfNum + 1,
                                     'd': distance,
                                     'axis': axis})

        if not response:
            return False
            
        return True

    def TiltAndReturn(self, args):
        """ This function Tilts one surface and optical axis should return to
        
        the original "X" direction after the tilted surface.
        
        args is a dict containing the arguments below:

        {
         'c'          : 0,
         'surfNum     : 1,
         'axis'       : 'y',
         'angle'      : '45',
        },

        where: 
            'c' is the configuration number
            'surfNum' is the index of the surface to be tilted
            'axis' is the the pivot axis. Should be one of "x" "y" or "z"
            'angle' is the tilt angle, in degree

        Returns True for success, False for error.

        """
        configuration = args['c']
        surfNum       = args['surfNum']
        axis          = args['axis']
        angle         = args['angle']

        originalSurfaces = self.GetSurfaces(configuration)

        codeVsurfNum = args['codeVsurfNum']

        # get the distance from the surface before and the surface being tilted
        distFromBefore = originalSurfaces[surfNum-1]['DistToNext']
        prevSurfType = originalSurfaces[surfNum-1]['TypeCode']
        distToNext = originalSurfaces[surfNum]['DistToNext']
        nextSurfType = originalSurfaces[surfNum+1]['TypeCode']

        if distFromBefore == 0 and prevSurfType in ['YT', 'XT', 'ZT']:
            response = self.ChaSurTil({'c': configuration,
                                       'n': surfNum - 1,
                                       'a': angle,
                                       'axis': axis})                           
        else:
            response = self.SurfaceTilt({'c': configuration,
                                         'n': surfNum - 1,
                                         'a': angle,
                                         'p': distFromBefore,
                                         'axis': axis})

        if not response :
            return False
        # apply tilt before and after the surface by the same angle
        # this makes sure the optical axis is pivoted by twice the angle
        
        if distToNext == 0 and nextSurfType in ['YT', 'XT', 'ZT']:
            response = self.ChaSurTil({'c': configuration,
                                       'n': surfNum + 1,
                                       'a': -angle,
                                       'axis': axis})
        elif distFromBefore == 0 and prevSurfType in ['YT', 'XT', 'ZT']:
            response = self.SurfaceTilt({'c': configuration,
                                        'n': surfNum,
                                        'a': -angle,
                                        'p': 0,
                                        'axis': axis})
        else:
            response = self.SurfaceTilt({'c': configuration,
                                        'n': surfNum + 1,
                                        'a': -angle,
                                        'p': 0,
                                        'axis': axis})

        if (platform.system() == "Windows"):
            self.Codev.DecenterAndReturn(str(codeVsurfNum))
            angle = str(angle)
            self.Codev.AddAlphaTilt(str(codeVsurfNum), angle)

        if not response:
            return False
        
        return True

    def TiltAndBend(self, args):
        """ This function Tilts one surface and rotates the optical axis 
        
        by twice of the surface tilt angle.
        
        This function should be used with reflective surfaces.

        args is a dict containing the arguments below:

        {
         'c'          : 0,
         'surfNum'    : 1,
         'axis'       : 'y',
         'angle'      : '45',
        },

        where: 
            'c' is the configuration number
            'surfnum' is the index of the surface to be tilted
            'axis' is the the pivot axis. Should be one of "x" "y" or "z"
            'angle' is the tilt angle, in degree

        Returns True for success, False for error.

        """
        configuration = args['c']
        surfNum       = args['surfNum']
        axis          = args['axis']
        angle         = args['angle']

        codeVsurfNum = args['codeVsurfNum']

        originalSurfaces = self.GetSurfaces(configuration)

        # get the distance from the surface before and the surface being tilted
        distFromBefore = originalSurfaces[surfNum-1]['DistToNext']
        prevSurfType = originalSurfaces[surfNum-1]['TypeCode']
        distToNext = originalSurfaces[surfNum]['DistToNext']
        nextSurfType = originalSurfaces[surfNum+1]['TypeCode']

        if distFromBefore == 0 and prevSurfType in ['YT', 'XT', 'ZT']:
            response = self.ChaSurTil({'c': configuration,
                                       'n': surfNum - 1,
                                       'a': angle,
                                       'axis': axis})              
        else:
            response = self.SurfaceTilt({'c': configuration,
                                         'n': surfNum - 1,
                                         'a': angle,
                                         'p': distFromBefore,
                                         'axis': axis})

        if not response :
            return False
        # apply tilt before and after the surface by the same angle
        # this makes sure the optical axis is pivoted by twice the angle
        
        if distToNext == 0 and nextSurfType in ['YT', 'XT', 'ZT']:
            response = self.ChaSurTil({'c': configuration,
                                       'n': surfNum + 1,
                                       'a': angle,
                                       'axis': axis})
        elif distFromBefore == 0 and prevSurfType in ['YT', 'XT', 'ZT']:
            response = self.SurfaceTilt({'c': configuration,
                                        'n': surfNum,
                                        'a': angle,
                                        'p': 0,
                                        'axis': axis})
        else:
            response = self.SurfaceTilt({'c': configuration,
                                        'n': surfNum + 1,
                                        'a': angle,
                                        'p': 0,
                                        'axis': axis})


        if (platform.system() == "Windows"):
            self.Codev.DecenterAndBend(str(codeVsurfNum))
            angle = str(angle)
            self.Codev.AddAlphaTilt(str(codeVsurfNum), angle)

        if not response:
            return False
        
        return True

    def ChaSurTil(self, args):
        """ Change the surface tilt angle of an exiting YT/XT/ZT surface

        """
        configuration = args['c']
        surfNum       = args['n']
        angle         = args['a']
        axis          = args['axis']

        originalSurfaces = self.GetSurfaces(configuration)

        surfaceType = originalSurfaces[surfNum]['TypeCode']

        if not surfaceType in ['YT', 'XT', 'ZT']:
            # not a YT/XT/ZT type surface, cannot change tilt angle
            return False

        resp = self.SurfaceTilt({'c': configuration,
                                 'n': surfNum,
                                 'a': angle,
                                 'p': 0,
                                 'axis': axis,})
        if not resp:
            return False

        resp = self.RemoveSurface(configuration, surfNum)

        if not resp:
            return False

        return True

    def ChaSurMov(self, args):
        """ Change decenter distance of an exiting YD/XD/ZD surface

        """
        configuration = args['c']
        surfNum       = args['n']
        dist          = args['d']
        axis          = args['axis']

        originalSurfaces = self.GetSurfaces(configuration)

        surfaceType = originalSurfaces[surfNum]['TypeCode']

        if not surfaceType in ['YD', 'XD', 'ZD']:
            # not a YD/XD/ZD type surface, cannot change distance
            return False

        resp = self.SurfaceMove({'c': configuration,
                                 'n': surfNum,
                                 'd': dist,
                                 'axis': axis,})
        if not resp:
            return False

        resp = self.RemoveSurface(configuration, surfNum)

        if not resp:
            return False

        return True

    def InsertFieldPoint(self,FieldType,ConfigurationNumber,y_Value,z_Value):
        """ Call Core to insert a new field point.

        Inputs:
            FieldType: "HFOV" (half field of view) or "FIH" (fractional image height)
            ConfigurationNumber:(starting from 0)
            y_Value and z_Value: 
                half-field-of-view values or fractional image heights of the field point

        return true if field point has been sucessfully added
        """

        if self.PrintDebugInfo:
            print('Sending request "InsertFieldPoint"')

        command = 'InsertFieldPoint {} {} {} {}'.format(
                                                        FieldType,
                                                        ConfigurationNumber,
                                                        y_Value,
                                                        z_Value,
                                                        )

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
        
    def RemoveFieldPoint(self,ConfigurationNumber,FieldNumber):
        """ Call Core to remove a field point.
        
        """

        if self.PrintDebugInfo:
            print('Sending request "RemoveFieldPoint"')

        command = 'RemoveFieldPoint {} {}'.format(ConfigurationNumber, FieldNumber)

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
        
    def ListFieldPoints(self, ConfigurationNumber):
        """ Return a list of tuples, each tuple contains y_value and z_value of the field point in terms of FIH
            This function needs updates to parse Pupil Shift Coeff. and Pupil Expasion Coeff
        """

        if self.PrintDebugInfo:
            print('Sending request "ListFieldPoints"')

        command = 'ListFieldPoints {}'.format(ConfigurationNumber)

        self.socket.send_string(command)
        FieldPoints = self.socket.recv_pyobj()

        return FieldPoints


    def SetFNumber(self, ParameterValue, plane='M'):
        """Set working F-number(equivalent F-number) of the system
        
        """

        if self.PrintDebugInfo:
            print('Sending request "SetFNumber"')

        self.socket.send_string("SetParameter QFN {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetImaFNumber(self, ParameterValue, plane='M'):
        """ Set the image-space F-number
        """

        if self.PrintDebugInfo:
            print('Sending request "SetImaFNumber"')

        self.socket.send_string("SetParameter XFN {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetImaFNumber(self, ParameterValue, plane='M'):
        """ Set the image-space F-number
        """

        if self.PrintDebugInfo:
            print('Sending request "SetImaFNumber"')

        self.socket.send_string("SetParameter XFN {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetObjectAngle(self, ParameterValue, plane='M'):
        """Set Object space half-angle for the system

        """
        if self.PrintDebugInfo:
            print('Sending request "SetObjectAngle')

        self.socket.send_string("SetParameter EAF {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False      

    def SetImageHeight(self, ParameterValue, plane='M'):
        """ Set the paraxial image height for the system

        """
        if self.PrintDebugInfo:
            print('Sending request "SetImageHeight')

        self.socket.send_string("SetParameter XCH {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False 

    def SetObjectHeight(self, ParameterValue, plane='M'):
        """ Set the object height for the system
        
        """

        if self.PrintDebugInfo:
            print('Sending request "SetObjectHeight')

        self.socket.send_string("SetParameter ECH {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False 
        
    def SetObjectDistance(self, ParameterValue, plane='M'):
        """ Set the object distance(from the first surface) 
            (Not working correctly for now)
        """

        if self.PrintDebugInfo:
            print('Sending request "SetObjectDistance')

        self.socket.send_string("SetParameter ECP {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetObjFNumber(self, ParameterValue, plane='M'):
        """ Set Object-space F-Number
            (Not working correctly for now)
        """

        if self.PrintDebugInfo:
            print('Sending request "SetObjFNumber')

        self.socket.send_string("SetParameter EFN {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetImaFNumber(self, ParameterValue, plane='M'):
        """ Set image-space F-Number

        """
        if self.PrintDebugInfo:
            print('Sending request "SetImaFNumber')

        self.socket.send_string("SetParameter XFN {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetImageDistance(self, ParameterValue, plane='M'):
        """ Set image distance of the system

        """      
        if self.PrintDebugInfo:
            print('Sending request "SetImageDistance')

        self.socket.send_string("SetParameter XCP {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetImageAngle(self, ParameterValue, plane='M'):
        """ Set image-space half-angle field

        """
        if self.PrintDebugInfo:
            print('Sending request "SetImageAngle')

        self.socket.send_string("SetParameter XAF {} {}".format(plane, ParameterValue))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetImageDistanceSolve(self, ConfigurationNumber, isSet=True):
        """ Set Image Distance Solve for the optical system
        
        """
        if self.PrintDebugInfo:
            print('Sending request "SetImageDistanceSolve"')
        
        message = 'yes' if isSet else 'no'

        self.socket.send_string("SetImageDistanceSolve {} {}".format(ConfigurationNumber, message))

        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetRotationalSymmetry(self, ConfigurationNumber, SymmetryCode):
        """ change the type of symmetry of the system.

        SymmetryCode is one of “RS”, “NRS”, “NSRT” (rotational symmetry, non-rotational symmetry and 

        non-symmetric ray tracing, respectively)

        """
        if self.PrintDebugInfo:
            print('Sending request "SetRotSym"')

        command = 'SetRotSym {} {}'.format(ConfigurationNumber, SymmetryCode)

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SetAberrationSymmetry(self, ConfigurationNumber, SymmetryCode):
        """ change the type of symmetry of aberrations (blurs).

        SymmetryCode is one of “SYM”, “ASYM” (rotational symmetry, asysmmetry, respectively)

        """
        if self.PrintDebugInfo:
            print('Sending request "SetAbeSym"')

        command = 'SetAbeSym {} {}'.format(ConfigurationNumber, SymmetryCode)

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def ChangeSystemClass(self, ConfigurationNumber, SystemType, plane="M"):
        """ Change the system class for the optical system

        SystemType is one of "OBJ", "CRL", "ARL", "TEL", "EYP", "AUF", "AUI"

        """
        if self.PrintDebugInfo:
            print('Sending request "ChaSysCla"')

        command = 'ChaSysCla {} {} {}'.format(ConfigurationNumber, plane, SystemType)

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def GetGeneralSystemSettings(self,ConfigurationNumber):
        """ Return a Dict containing all system setting infomation:

        {
            'ImageDistanceSol': 'On', 
            'SystemType (M)': 'Objective',
            'RotationalSym': 'RotationallySymmetric', 
            'AberrationSym': 'Symmetric', 
            'PupilShape': 'CircularOrElliptical', 
            'SystemSetup': 'Collinear', 
            'CoordinateSys': 'Standard',
        }

        """
        if self.PrintDebugInfo:
            print('Sending request "GetGenSysSet"')

        command = 'GetGenSysSet {}'.format(ConfigurationNumber)

        self.socket.send_string(command)
        Settings = self.socket.recv_pyobj()

        return Settings

    def GetEntrancePupilSize(self,ConfigurationNumber,plane='M'):
        """ Return entrance pupil size.

        """

        if self.PrintDebugInfo:
            print('Sending request "GetEntrancePupilSize"')

        command = 'GetFirstOrderParameter {} {} EPS'.format(ConfigurationNumber, plane)

        self.socket.send_string(command)
        EntrancePupilSize = self.socket.recv_pyobj()

        return EntrancePupilSize

    def GetEntrancePupilDistance(self,ConfigurationNumber,plane='M'):
        """ Return the distance from the first surface to the entrance pupil

        """
        if self.PrintDebugInfo:
            print('Sending request "GetEntrancePupilDistance"')

        command = 'GetFirstOrderParameter {} {} EPD'.format(ConfigurationNumber, plane)

        self.socket.send_string(command)
        EntPupDis = self.socket.recv_pyobj()

        return EntPupDis

    def GetExitPupilSize(self,ConfigurationNumber,plane='M'):
        """ Return exit pupil size.

        """

        if self.PrintDebugInfo:
            print('Sending request "GetExitPupilSize"')

        command = 'GetFirstOrderParameter {} {} XPS'.format(ConfigurationNumber, plane)

        self.socket.send_string(command)
        ExitPupilSize = self.socket.recv_pyobj()

        return ExitPupilSize

    def GetExitPupilDistance(self,ConfigurationNumber,plane='M'):
        """ Return the distance from the last surface to the exit pupil

        """
        if self.PrintDebugInfo:
            print('Sending request "GetExitPupilDistance"')

        command = 'GetFirstOrderParameter {} {} XPD'.format(ConfigurationNumber, plane)

        self.socket.send_string(command)
        ExiPupDis = self.socket.recv_pyobj()

        return ExiPupDis

    def GetFNumber(self,ConfigurationNumber,plane='M'):
        """ Returns F number 
        
        """

        if self.PrintDebugInfo:
            print('Sending request "GetFNumber"')

        command = 'GetFirstOrderParameter {} {} QFN'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        FNumber = self.socket.recv_pyobj()

        return FNumber

    def GetObjFNumber(self,ConfigurationNumber,plane='M'):
        """ Return Object-space F number

        """
        if self.PrintDebugInfo:
            print('Sending request "GetObjFNumber"')

        command = 'GetFirstOrderParameter {} {} EFN'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        FNumber = self.socket.recv_pyobj()

        return FNumber

    def GetImaFNumber(self,ConfigurationNumber,plane='M'):
        """ Return image-space F number

        """
        if self.PrintDebugInfo:
            print('Sending request "GetImaFNumber"')

        command = 'GetFirstOrderParameter {} {} XFN'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        FNumber = self.socket.recv_pyobj()

        return FNumber

    def GetFocalLength(self,ConfigurationNumber,plane='M'):
        """ Return equivalent focal length

        """
        if self.PrintDebugInfo:
            print('Sending request "GetFocalLength"')

        command = 'GetFirstOrderParameter {} {} EQUFOCLEN'.format(ConfigurationNumber,plane)
        
        self.socket.send_string(command)
        FocalLength = self.socket.recv_pyobj()

        return FocalLength

    def GetUnit(self,ConfigurationNumber,plane='M'):
        """ Returns the unit of the system
        
        """

        if self.PrintDebugInfo:
            print('Sending request "GetUnit"')

        command = 'GetFirstOrderParameter {} {} UNI'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        Unit = self.socket.recv_pyobj()

        return Unit

    def GetObjectAngle(self,ConfigurationNumber,plane='M'):
        """ Returns the object-space half-angle field

        """
        if self.PrintDebugInfo:
            print('Sending request "GetObjectAngle"')

        command = 'GetFirstOrderParameter {} {} EAF'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        ObjectAngle = self.socket.recv_pyobj()

        return ObjectAngle

    def GetObjectDistance(self,ConfigurationNumber,plane='M'):
        """ Returns the object distance (measured from the first surface)

        """
        if self.PrintDebugInfo:
            print('Sending request "GetObjectDistance"')

        command = 'GetFirstOrderParameter {} {} ECP'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        ObjectDistance = self.socket.recv_pyobj()

        return ObjectDistance

    def GetObjectHeight(self,ConfigurationNumber,plane='M'):
        """ Returns the object height

        """
        if self.PrintDebugInfo:
            print('Sending request "GetObjectHeight"')

        command = 'GetFirstOrderParameter {} {} ECH'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        ObjectHeight = self.socket.recv_pyobj()

        return ObjectHeight

    def GetImageAngle(self,ConfigurationNumber,plane='M'):
        """ Return image space half-angle field

        """
        if self.PrintDebugInfo:
            print('Sending request "GetImageAngle"')

        command = 'GetFirstOrderParameter {} {} XAF'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        ImageAngle = self.socket.recv_pyobj()

        return ImageAngle

    def GetImageHeight(self,ConfigurationNumber,plane='M'):
        """ Returns the paraxial image height

        """

        if self.PrintDebugInfo:
            print('Sending request "GetImageHeight"')

        command = 'GetFirstOrderParameter {} {} XCH'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        ImageHeight = self.socket.recv_pyobj()

        return ImageHeight
    
    def GetName(self,ConfigurationNumber,plane='M'):
        """ Return name of the system

        """

        if self.PrintDebugInfo:
            print('Sending request "GetName"')

        command = 'GetFirstOrderParameter {} {} NAM'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        Name = self.socket.recv_pyobj()

        return Name

    def GetLateralMagnification(self,ConfigurationNumber,plane='M'):
        """ Return the lateral magnification 

        """

        if self.PrintDebugInfo:
            print('Sending request "GetLateralMagnification"')

        command = 'GetFirstOrderParameter {} {} LATMAG'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        LatMag = self.socket.recv_pyobj()

        return LatMag

    def GetOverallLength(self,ConfigurationNumber,plane='M'):
        """ Return Vertex-to-Vertex distance of the entire system

        """

        if self.PrintDebugInfo:
            print('Sending request "GetOverallLength"')

        command = 'GetFirstOrderParameter {} {} VTV'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        OverallLength = self.socket.recv_pyobj()

        return OverallLength

    def GetFSPosition(self,ConfigurationNumber,plane='M'):
        """ Return the Surface where the field stop is located
        
        """

        if self.PrintDebugInfo:
            print('Sending request "GetFSPosition"')
        
        command_asd = 'GetFirstOrderParameter {} {} FSD'.format(ConfigurationNumber,plane)
        command_asn = 'GetFirstOrderParameter {} {} FSN'.format(ConfigurationNumber,plane)

        self.socket.send_string(command_asd)
        distance = self.socket.recv_pyobj()

        self.socket.send_string(command_asn)
        surf_num = int(self.socket.recv_pyobj())

        unit = self.GetUnit(ConfigurationNumber,plane)

        if float(distance) == 0:
            return "Surface #{}".format(surf_num)

        else:
            return "{}{} after surface #{}".format(distance, unit, surf_num)

    def GetFSSize(self,ConfigurationNumber,plane='M'):
        """ Return the size of the field stop

        """
        if self.PrintDebugInfo:
            print('Sending request "GetFSSize"')

        command = 'GetFirstOrderParameter {} {} FSS'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        Size = self.socket.recv_pyobj()

        return Size

    def GetASPosition(self,ConfigurationNumber,plane='M'):
        """ Return the position where paraxial chief rays intersect with the optical axis
    
        """

        if self.PrintDebugInfo:
            print('Sending request "GetASPosition"')
        
        command_asd = 'GetFirstOrderParameter {} {} ASD'.format(ConfigurationNumber,plane)
        command_asn = 'GetFirstOrderParameter {} {} ASN'.format(ConfigurationNumber,plane)

        self.socket.send_string(command_asd)
        distance = self.socket.recv_pyobj()

        self.socket.send_string(command_asn)
        surf_num = int(self.socket.recv_pyobj())

        unit = self.GetUnit(ConfigurationNumber,plane)

        if float(distance) == 0:
            return "Surface #{}".format(surf_num)

        else:
            return "{}{} after surface #{}".format(distance, unit, surf_num)

    def SetASPosition(self,ConfigurationNumber,SurfaceNumber=None):
        """ Set the paraxial chief ray axial intersection by specifying the surfaceNumber

        Set SurfaceNumber to -1 for telecentric paraxial chief ray in image space
        
        """
        if SurfaceNumber == None:
            Option = "Free"
        elif SurfaceNumber == -1:
            Option = "Telecentric"
        else:
            Option = SurfaceNumber

        if self.PrintDebugInfo:
            print('Sending request "GetASPostion"')

        command = 'ParEntPup {} {}'.format(ConfigurationNumber,Option)

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def GetASSize(self,ConfigurationNumber,plane='M'):
        """ Return the size of the aperture stop

        """
        if self.PrintDebugInfo:
            print('Sending request "GetASSize"')

        command = 'GetFirstOrderParameter {} {} ASS'.format(ConfigurationNumber,plane)

        self.socket.send_string(command)
        Size = self.socket.recv_pyobj()

        return Size

    def GetWavelengths(self,ConfigurationNumber):
        """ Return a list containing the wavelengths of the system

        """
        if self.PrintDebugInfo:
            print('Sending request "GetWavelengths"')

        command = 'GetWavelengths {}'.format(ConfigurationNumber)

        self.socket.send_string(command)
        Wavelengths = self.socket.recv_pyobj()

        return Wavelengths

    def SetWavelengths(self,ConfigurationNumber,Wavelengths,updateIndex=True):
        """ Set the three wavelengths of the system

        Back-end usage : <CONFIGURATION NUMBER> <BASIC> <SHORT> <LONG> [R|C]
        
        Wavelengths is a list containing three wavelengths in the same order as in the 
            back end command:
            [wavelength #1, wavelength #2, wavelength #3]

        The element could be set to zero if you want to keep that wavelength unchanged  

        updateIndex is a flag deciding whether refractive index will be recalculated.
        
        """
        if self.PrintDebugInfo:
            print('Sending request "SetWavelengths"')

        if updateIndex == True:
            option = "R"
        else:
            option = "C"

        command = 'SetWavelengths {} {} {} {} {}'.format(
                                                    ConfigurationNumber,
                                                    Wavelengths[0],
                                                    Wavelengths[1],
                                                    Wavelengths[2],
                                                    option)

        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False

    def SaveSystem(self,FileName,overwrite=True):
        """ Saves the system .A file in the Eikonal back end.

        """

        if self.PrintDebugInfo:
            print('Sending request "SaveSystem"')

        command = 'SaveSystem {} {}'.format(FileName,overwrite)
        self.socket.send_string(command)
        response = self.socket.recv_pyobj()

        if response == 'OK':
            return True
        else:
            return False
        
    def ParseSeq(self, filename):
        """ Call ParseSeq in SeqObject Class

        """
        if (platform.system() == "Windows"):
            self.Codev.LoadOpticalSystem(filename)
        return SeqObject(self).ParseSeq(filename)
    
    def WriteSeq(self, filename):
        """ export seqnece file """

        return SeqObject(self).WriteSeq(filename)

    def BasicDecenterCodeV(self, surfaceNumber, angle, isTilted, tiltType):
        if (platform.system() == "Windows"):
            self.Codev.BasicDecenter(surfaceNumber, isTilted, tiltType)
            self.Codev.AddAlphaTilt(surfaceNumber, angle) 

    def ChangeZernikeCoefficients(self,typeCode,args):
        if (platform.system() == "Windows"):
            surfaceNumber = args["codeVsurfaceNumber"]
            if (typeCode != "ZR"):
                self.Codev.ChangeSurfaceToZernike(surfaceNumber)
            self.Codev.SetZernikeCoefficients(args)    

    if (platform.system() == "Windows"):
        def GetFFD(self, filename, ffdScale, xangle, yangle,aberration):
            resp = self.Codev.PlotFFD(ffdScale, xangle, yangle,aberration)
            return resp  
        def ChangeTerm(self,surfacenumber,zerniketerm,zernikevalue):
            resp = self.Codev.SetZernikeTerm(surfacenumber,int(zerniketerm),zernikevalue)    
            return resp




if __name__ == "__main__":
   # For debugging

   print("Printing debugging messages: " + self.PrintDebugInfo)
