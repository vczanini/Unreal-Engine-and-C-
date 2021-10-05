import time
import pickle
from pprint import pprint
from EikonalInterfaceLayer import Interface as eil

# Start the Core, and then run this script:
#
#  python EIL-test.py
#
# If you get errors, make sure that all config files exist and are correct.
#
# This loads a system and asks for information about it.
#
# NOTE: There are two methods of using the Interface layer below: the Command()
# method and calling Interface methods directly.  Look at the output from this
# script to see what objects / strings are returned in each case.

################################################################################
#                                                                              #
# Use of the Interface.Command() method.  This is used to send commands as     #
# strings to the Interface layer.                                              #
#                                                                              #
################################################################################

commands = [
            'LoadSystem 111111.DBS',
            'GetNumSurfaces 0',
            'GetSurfaces 0',
            'GetRays 0 5 5',
           ]

il = eil(True)
time.sleep(2)

# Run the IL's internal speed test (string echo from IL to Core and back).

print('==============================================================')
print('\nIO<-->Core echo speed test...')
args={'iterations':100,'messageSize':1000}
timePerCall = il.SpeedTest(args)
print('EIL had an average round-trip time of: {} ms'.format(timePerCall))

# Do a local speed test, asking the Core for some data each time.

print('==============================================================')
print('\nFull EIL-test<-->IL<-->Core command-response speed test...')
iterations    = 100
startTime     = time.time()
loadCmd       = 'LoadSystem 111111.DBS'
print('Loading system...')
resp          = il.Command(loadCmd)
print('resp: {}'.format(resp))
repetitiveCmd = 'GetRays 0 5 5'
il.PrintDebugInfo = False
for call in range(iterations):
    resp = il.Command(repetitiveCmd)
totalTime = time.time() - startTime
avgTime = 1000.0 * totalTime / (call + 1)
print('Average time per command ({}) is {} ms'.format(repetitiveCmd,avgTime))
il.PrintDebugInfo = True
print('==============================================================')

for cmd in commands:

    print('==============================================================')
    print('Sending command: "{}"'.format(cmd))

    resp = il.Command(cmd)

    # Check the type of the response.

    if isinstance(resp,str):

        # We received a string instead of a serialized Python object.
        input('Received string response: "{}"{}\nPress enter.'.\
                format(resp[:70],
                       {True:'',False:'...'}[len(resp)<70]))

    else:

        input('Received {} type response.'
                '\nPress enter to see response:'.format(type(resp)))
        pprint(resp)


################################################################################
#                                                                              #
# An better alternative to sending a text command to the Interface layer using #
# the Command() function is to call its methods directly.                      #
#                                                                              #
################################################################################

###############################
# Insert a refractive surface #
# (spherical)                 #
###############################

print('')
args = {
        'c'    : 0,     # config
        's'    : 3,     # surface
        'r'    : 20,    # new radius
        'dp'   : 3.5,   # new dist from prev
        'dn'   : 4.5,   # new dist to next
        'gl'   : 'SF57',# new glass
        'type' : 'refractive',
       }
resp = il.InsertSurface(args)
print('Response to InsertSurface: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetSurfaces(0)
print('Updated surfaces:\n{}'.format(resp))

###############################
# Change a refractive surface #
# The reflective & refractive #
# should be consolidated into #
# one command with 'type'     #
# option.                     #
###############################

print('')
args = {
        'c'  : 0,     # config
        's'  : 4,     # surface
        'r'  : 10,    # new radius
        'dp' : 2.5,   # new dist from prev
        'dn' : 3.0,   # new dist to next
        'gl' : 'BK7', # new glass
       }
resp = il.ChangeRefractiveSurface(args)
print('Response to ChangeRefractiveSurface: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetSurfaces(0)
print('Updated surfaces:\n{}'.format(resp))

###############################
# Insert a reflective surface #
# (spherical)                 #
###############################

print('')
args = {
        'c'    : 0,     # config
        's'    : 4,     # surface
        'r'    : 50,    # new radius
        'dp'   : 2.9,   # new dist from prev
        'dn'   : 3.2,   # new dist to next
        'type' : 'reflective',
       }
resp = il.InsertSurface(args)
print('Response to InsertSurface: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetSurfaces(0)
print('Updated surfaces:\n{}'.format(resp))

###############################
# Change a reflective surface #
# The reflective & reflective #
# should be consolidated into #
# one command with 'type'     #
# option.                     #
###############################

print('')
args = {
       'c'  : 0,     # config
       's'  : 5,     # surface
       'r'  : 23,    # new radius
       'dp' : 2.9,   # new dist from prev
       'dn' : 3.4,   # new dist to next
      }
resp = il.ChangeReflectiveSurface(args)
print('Response to ChangeReflectiveSurface: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetSurfaces(0)
print('Updated surfaces:\n{}'.format(resp))

###############################
# Example: insert an aperture #
# stop                        #
###############################

print('')
args = {
        'c'  :0,        # config
        's'  :2,        # surface
        'dp' :1.2,      # dist from prev
        'dn' :2.8,      # dist to next
        }
resp = il.InsertApertureStop(args)
print('Response to InsertApertureStop: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
il.Command('$eval')
resp1 = il.Command('GetFirstOrderParameter 0 m asn')
resp2 = il.Command('GetFirstOrderParameter 0 m asd')
print('Current Stop position: {} mm from S#{} '.format(resp2, resp1))

####################################
# Example: insert an aperture stop #
# without calling ParEntPup        #
####################################
args = {
        'c'  :0,        # config
        's'  :5,        # surface
        'dp' :1.2,      # dist from prev
        'dn' :2.8,      # dist to next
        }
resp = il.InsertApertureStop(args,setParEntPup=False)
print('Response to InsertApertureStop (No paraxial entrance pupil control):\
"{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
il.Command('$eval')
resp1 = il.Command('GetFirstOrderParameter 0 m asn')
resp2 = il.Command('GetFirstOrderParameter 0 m asd')
print('Current Stop position: {} mm from S#{} '.format(resp2, resp1))

###############################
# Example: change position of #
# an aperture stop            #
###############################

print('')
args = {
        'c'  :0,        # config
        's'  :3,        # surface
        'dp' :1.5,      # new dist from prev
        'dn' :3.5,      # new dist to next
        }
resp = il.ChangeApertureStop(args)
print('Response to ChangeApertureStop: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
il.Command('$eval')
resp1 = il.Command('GetFirstOrderParameter 0 m asn')
resp2 = il.Command('GetFirstOrderParameter 0 m asd')
print('Current Stop position: {} mm from S#{} '.format(resp2, resp1))

###########################################
# Example: change position of an aperture #
# stop without calling ParEntPup          #
###########################################
print('')
args = {
        'c'  :0,        # config
        's'  :2,        # surface
        'dp' :1.5,      # new dist from prev
        'dn' :3.5,      # new dist to next
        }
resp = il.ChangeApertureStop(args,setParEntPup=False)
print('Response to ChangeApertureStop (No paraxial entrance pupil control):\
: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
il.Command('$eval')
resp1 = il.Command('GetFirstOrderParameter 0 m asn')
resp2 = il.Command('GetFirstOrderParameter 0 m asd')
print('Current Stop position: {} mm from S#{} '.format(resp2, resp1))

################################
# Example: insert a refractive #
# surface defined by a Zernike #
# polynomial.                  #
################################


args = {
        'c'     : 0,
        'p'     : 3,
        'r'     : 3.4,
        'dp'    : 2.0,
        'dn'    : 3.0,
        'su'    : 4.0,
        'an'    : [0.0,0.3,0.0,0.4,0.0,0.0,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,\
                   0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,\
                   0.0,0.0,0.0,0.0,0.0],
        'b'     : 'BK7',
       }

print('')
args['type'] = 'refractive'
resp = il.InsertZernike(args)
print('Response to InsertZernike for refractive sfc: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

################################
# Example: decenter a surface  #
################################


args = {
        'c'     : 0,
        'n'     : 1,
        'd'     : 0.2,
        'axis'  : 'y',
       }

print('')
resp = il.SurfaceMove(args)
print('Response to SurfaceMove: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

################################
# Example: tilt a surface      #
################################


args = {
        'c'     : 0,
        'n'     : 1,
        'a'     : -15,
        'p'     : 0,
        'axis'  : 'y',
       }

print('')
resp = il.SurfaceTilt(args)
print('Response to SurfaceTilt: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

####################################
# Change the Zern refractive surf  #
####################################

args = {
        'c'     : 0,
        'p'     : 4,
        'r'     : 10.0,
        'dp'    : 3.0,
        'dn'    : 4.0,
        'su'    : 9.0,
        'an'    : [0.0,0.5,0.0,0.7,0.0,0.0,0.1,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,\
                   0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,\
                   0.0,0.0,0.0,0.0,0.0],
        'b'     : 'NSF66',
       }

print('')
args['type'] = 'refractive'
resp = il.ChangeZernike(args)
print('Response to ChangeZernike for refractive sfc: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

###############################
# Add a Zern reflective surf  #
###############################

args['type'] = 'reflective'
resp         = il.InsertZernike(args)
print('Response to InsertZernike for reflective sfc: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

####################################
# Change the Zern reflective surf  #
####################################

args = {
        'c'     : 0,
        'p'     : 5,
        'r'     : 10.0,
        'dp'    : 3.0,
        'dn'    : 4.0,
        'su'    : 9.0,
        'an'    : [0.0,0.5,0.0,0.7,0.0,0.0,0.1,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,\
                   0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,\
                   0.0,0.0,0.0,0.0,0.0],
       }

print('')
args['type'] = 'reflective'
resp = il.ChangeZernike(args)
print('Response to ChangeZernike for reflective sfc: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

#################################
# Change the reference surface  #
#################################

args = {'c'     : 0,
        'dn'    : 0,
        'gl'    : 'AIR'
        }

print('')
resp = il.ChangeReferenceSurface(args)
print('Response to ChangeRefenceSurface: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

###############################
# Get a table of surf data    #
###############################

resp = il.GetSurfaceDataTable('return')
input('Requested surface data table.  Enter to see response:')
print('{}'.format(resp))

####################################
# Show all surfaces in a global    #
# coordinate system, with respect  #
# to a selected reference surface. #
####################################

args = {
        'c'  : 0, # configuration number
        'rs' : 3, # reference surface for coordinates
       }
resp = il.GetSurfacesGlobal(args)
input('Requested surfaces in global coordinates.  Enter to see response:')
print('{}'.format(resp))

###############################
# Test echo on/off.  This     #
# requires monitoring the     #
# stdout of the Core by eye.  #
###############################

# Test echo on/off.  This requires monitoring the stdout of the Core by eye.
print('')
input('Press Enter to see echo tests:')
args = {'echo':True}
print('Setting Core echo on...')
resp = il.SetCoreEcho(args)
print('Response to SetCoreEcho: "{}"'.format(resp))
stringMessage = 'Hello World!'
print('You should see "{}" in the stdout stream of Core.'.format(stringMessage))
cmd = 'PrintToStdout {}'.format(stringMessage)
resp = il.Command(cmd)
print('Response to PrintToStdout: "{}"'.format(resp))
args = {'echo':False}
print('Setting Core echo off...')
resp = il.SetCoreEcho(args)
print('Response to SetCoreEcho: "{}"'.format(resp))

print('\n\nLeaving the Core running.\n')

# input('Enter to stop the Core and quit.')
# il.Stop()

print('Response to GetImageHeight: {}'.format(resp))

############################
#  Insert a field point    # 
############################

print('')
resp = il.InsertFieldPoint('HFOV', 0, 10, 0)
print('Response to InsertFieldPoint (field type: HFOV): "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.ListFieldPoints(0)
print('Updated field points: \n{}'.format(resp))
print('')
resp = il.InsertFieldPoint('FIH', 0, 0.3, 0)
print('Response to InsertFieldPoint (field type: FIH): "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.ListFieldPoints(0)
print('Updated field points: \n{}'.format(resp))

############################
#  Remove a field point    # 
############################

print('')
resp = il.RemoveFieldPoint(0,1)
print('Response to RemoveFieldPoint: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.ListFieldPoints(0)
print('Updated field points: \n{}'.format(resp))

###############################
# Test SetImageDistanceSolve  #
#                             #
###############################
resp = il.SetImageDistanceSolve(0, True)
print('Response to SetImageDistanceSolve: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.SetImageDistanceSolve(0, False)
print('Response to SetImageDistanceSolve: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

##########################
# Test Set/GetASPosition #
# & GetFSPostion         #
##########################
print('')
resp = il.SetASPosition(0, -1) #telecentric paraxial chief ray in image space
print('Response to SetASposition(Telecentric): "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetImageAngle(0)
print('Resonese to GetImageAngle: {}, should be equal to 0'.format(resp))
resp = il.SetASPosition(0, 4)
print('Response to SetASposition(Surface #4): "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetASPosition(0)
print('Resonese to GetASPostion: {}'.format(resp))
resp = il.GetFSPosition(0)
print('Resonese to GetFSPostion: {}'.format(resp))

############################################
# Test SetParameter & GetFirOrdParameter   #
############################################

print('')
resp = il.SetFNumber(5)
print('Response to SetFNumber: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetFNumber(0)
print('Response to GetFNumber: {}'.format(resp))

resp = il.SetImaFNumber(4.8)
print('Response to SetImaFNumber: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetImaFNumber(0)
print('Response to GetImaFNumber: {}'.format(resp))

resp = il.SetImageHeight(15)
print('Response to SetImageHeight: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetImageHeight(0)
print('Response to GetImageHeight: {}'.format(resp))

resp = il.SetObjectAngle(30)
print('Response to SetObjectAngle: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetObjectAngle(0)
print('Response to GetObjectAngle: {}'.format(resp))

print('')
print('Changing Symmetry Flag to "Non-Rotational Symmetry"..')
il.Command("SETROTSYM 0 NRS")

resp = il.SetFNumber(4.8, 'E')
print('Response to SetFNumber on equatorial plane : "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetFNumber(0, 'E')
print('Response to GetFNumber on equatorial plane: {}'.format(resp))

resp = il.SetImaFNumber(4.5, 'E')
print('Response to SetImaFNumber on equatorial plane : "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetImaFNumber(0, 'E')
print('Response to GetImaFNumber on equatorial plane: {}'.format(resp))

resp = il.SetImageHeight(14.7, 'E')
print('Response to SetImageHeight on equatorial plane: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetImageHeight(0, 'E')
print('Response to GetImageHeight on equatorial plane: {}'.format(resp))

resp = il.SetObjectAngle(35, 'E')
print('Response to SetObjectAngle on equatorial plane: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetObjectAngle(0, 'E')
print('Response to GetObjectAngle on equatorial plane: {}'.format(resp))

print('')
resp_m = il.GetEntrancePupilSize(0)
resp_e = il.GetEntrancePupilSize(0,'E')
print('Response to GetEntrancePupilSize: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetEntrancePupilDistance(0)
resp_e = il.GetEntrancePupilDistance(0,'E')
print('Response to GetEntrancePupilDistance: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetExitPupilSize(0)
resp_e = il.GetExitPupilSize(0,'E')
print('Response to GetExitPupilSize: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetExitPupilDistance(0)
resp_e = il.GetExitPupilDistance(0,'E')
print('Response to GetExitPupilDistance: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetFocalLength(0)
resp_e = il.GetFocalLength(0,'E')
print('Response to GetFocalLength: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetUnit(0)
resp_e = il.GetUnit(0,'E')
print('Response to GetUnit: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetOverallLength(0)
resp_e = il.GetOverallLength(0,'E')
print('Response to GetOverallLength: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetASSize(0)
resp_e = il.GetASSize(0,'E')
print('Response to GetASSize: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

resp_m = il.GetFSSize(0)
resp_e = il.GetFSSize(0,'E')
print('Response to GetFSSize: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

###########################
# Test ChangeSystemClass  #
###########################

print('')
resp_m = il.ChangeSystemClass(0, 'OBJ')
resp_e = il.ChangeSystemClass(0, 'ARL', 'E')
print('Response to ChangeSystemClass: Meridional plane: {}, Equatorial plane: {}'.format(resp_m,resp_e))

print('')
resp = il.GetGeneralSystemSettings(0)
print('{"SystemType (M)": "Objective"} and {"SystemType (E)": "AfocalRelay"} should be in the following dictionary')
print('Response to GetgeneralSystemSettings:\n {}'.format(resp))

######################################
# SetParameter & GetFirOrdParameter  #
# for Common Relay System           #
######################################
print("")
filename = "tbse.a"
print("Loading lens {}...".format(filename))
il.LoadSystem(filename) # load a singlet for testing.

resp = il.GetLateralMagnification(0)
print('Response to GetLateralMagnification: {}'.format(resp))


resp = il.SetObjectDistance(-90)
print('Response to SetObjectDistance: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetObjectDistance(0)
print('Response to GetObjectDistance: {}'.format(resp))

resp = il.SetObjectHeight(-10)
print('Response to SetObjectHeight: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetObjectHeight(0)
print('Response to GetObjectHeight: {}'.format(resp))

resp = il.SetImaFNumber(5) # set image-space f-number
print('Response to SetImaFNumber: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetImaFNumber(0)
print('Response tp GetImaFNumber: {}'.format(resp))

resp = il.SetObjFNumber(5) # set object-space f-number 
print('Response to SetObjFNumber: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetObjFNumber(0)
print('Response tp GetObjFNumber: {}'.format(resp))

##############################
# Test SetRotSym/SetAbeSym   #     
##############################

print('')
resp = il.SetRotationalSymmetry(0, "NRS")
print('Response to SetRotationalSymmetry: {}'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.SetAberrationSymmetry(0, "ASYM")
print('Response to SetAberrationSymmetry: {}'.format(resp,{True:'Success',False:'Failure'}[resp]))

########################
# Test GetGenSysSet    #
########################

print('')
resp = il.GetGeneralSystemSettings(0)
print('Response to GetgeneralSystemSettings:\n {}'.format(resp))

########################
# Test GetWavelengths  #
# and SetWavelengths   #
########################

print('')
resp = il.SetWavelengths(0,[0.4,0.3,0.5])
print('Response to SetWavelengths: {}'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetWavelengths(0)
print('Response to GetWavelengths:\n {}'.format(resp))

########################
# Test MoveAndReturn   #
# and TiltAndReturn    #
########################
il.LoadSystem('TRIPLET.A')
print('')
resp = il.MoveAndReturn({'c': 0, 'surfNum': 4, 'axis': 'y', 'dist': 1})
print('Response to MoveAndReturn: {}'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.TiltAndReturn({'c': 0, 'surfNum': 5, 'axis': 'y', 'angle': 5})
print('Response to TiltAndReturn: {}'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetSurfaceDataTable()
print(resp)

########################
# Test MoveAndBend     #
# and TiltAndBend      #
########################
print('')
resp = il.MoveAndBend({'c': 0, 'surfNum': 10, 'axis': 'y', 'dist': 3})
print('Response to MoveAndBend: {}'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.TiltAndBend({'c': 0, 'surfNum': 11, 'axis': 'y', 'angle': 10})
print('Response to TiltAndBend: {}'.format(resp,{True:'Success',False:'Failure'}[resp]))
resp = il.GetSurfaceDataTable()
print(resp)

######################
# Test Save System   #
######################

resp = il.SaveSystem("Test.A")
print('Response to SaveSystem: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

######################
# Test ParseSeq      #
######################

resp = il.ParseSeq("./testing/ag_triplet.seq")
print('Response to ParseSeq: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

il.LoadSystem("./testing/ag_triplet.A")
resp = il.GetSurfaceDataTable()
print("ag_triplet.A:")
print(resp)

#############################
# Test ParseSeq for finite  #
# conjugate system#         #
#############################

resp = il.ParseSeq("./testing/triplet_finite_objdis.seq")
print('Test for a common relay system')
print('Response to ParseSeq: "{}" ({})'.format(resp,{True:'Success',False:'Failure'}[resp]))

il.LoadSystem("./testing/triplet_finite_objdis.A")
dist = il.GetObjectDistance(0)

print('Object distance is {} mm ({})'.format(dist,'Success' if dist == -150 else 'Failure'))
resp = il.GetSurfaceDataTable()
print("Surface data table:\n")
print(resp)