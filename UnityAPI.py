# Sifan Ye
# sye8 at u dot rochester dot edu
#
# The Unity API
# Run this before Unity application is run

import json
import subprocess
import sys

import zmq

from EikonalInterfaceLayer import Interface as eil



# Fire up the Core
coreProcess = subprocess.Popen(["python3", "src/Core.py"])
il = eil(True)

# Init ROUTER
context = zmq.Context()
router = context.socket(zmq.ROUTER)
router.bind("tcp://*:5558")
# Init Poller
poller = zmq.Poller()
poller.register(router, zmq.POLLIN)


# Cleanup Function
def cleanup():
    print("Closing core")
    il.Stop()
    print("Closing router")
    router.close()
    context.term()


# Socket Loop
try:
    while True:

        sockets = dict(poller.poll())
        
        if router in sockets:
            clientID, msg = router.recv_multipart()
            args = msg.decode().split()
        
            if args[0] == "cmd":
                cmd = " ".join(args[1:])
                resp = il.Command(cmd)

                # Send to Unity
                toSend = ""
                if isinstance(resp,str):
                    toSend = resp
                else:
                    toSend = json.dumps(resp)
                router.send_multipart([clientID, toSend.encode()])
            elif args[0] == "interface":
                rays = []
                surfaces = []
                if args[1] == "SlideAndRayTrace":
                    cmdArgs = {"configNum"           : args[2],
                               "firstSurf"            : args[3],
                               "lastSurf"             : args[4],
                               "rangeOfMov"           : args[5],
                               "numberOfPositions"    : args[6],
                               "QFN"                  : args[7]}
                    resp = il.SlideAndRayTrace(cmdArgs)
                    router.send_multipart([clientID, resp.encode()])
                elif args[1] == "ParseSeq":
                    il.ParseSeq(args[2])   
                    cmd = "LoadSystem " + args[2].split(".")[0] +".A"
                    resp = il.Command(cmd)
                    rep = il.GetGeneralSystemSettings(0)
                    if (rep["RotationalSym"] == "RotationallySymmetric"):
                        re = "RotationallySymmetric " + str(il.GetObjectAngle(0,'M')) + " " + str(len(il.ListFieldPoints(0)))
                    else:
                        re = "RotationallyAsymmetric " + str(il.GetObjectAngle(0,'M')) +" " + str(il.GetObjectAngle(0,'E')) + " " + str(len(il.ListFieldPoints(0))) 
                    # Send to Unity
                    toSend = ""
                    if isinstance(re,str):
                        toSend = re
                    else:
                        toSend = json.dumps(re)
                    router.send_multipart([clientID, toSend.encode()])
                elif args[1] == "GetFFD":
                    if (args[5] == "RotationallySymmetric"):
                        yangle = xangle = args[6]
                    else:
                        yangle = args[6]
                        xangle = args[7]    
                    toSend = il.GetFFD(args[2],args[3],xangle,yangle,args[4])
                    router.send_multipart([clientID, toSend.encode()])    
                elif args[1] == "TiltAndBend":
                    cmdArgs = { "c"       : int(args[2]),
                                "surfNum" : int(args[3]),
                                "axis"    : args[4],
                                "angle"   : float(args[5]),
                                "codeVsurfNum" : args[6]}
                    toSend = il.TiltAndBend(cmdArgs)
                    if toSend == True:
                        toSend ="True"
                    else:
                        toSend ="False"    
                    router.send_multipart([clientID, toSend.encode()])   
                elif args[1] == "TiltAndReturn":
                    cmdArgs = { "c"       : int(args[2]),
                                "surfNum" : int(args[3]),
                                "axis"    : args[4],
                                "angle"   : float(args[5]),
                                "codeVsurfNum" : args[6]}
                    toSend = il.TiltAndReturn(cmdArgs)
                    if toSend == True:
                        toSend ="True"
                    else:
                        toSend ="False"    
                    router.send_multipart([clientID, toSend.encode()])
                elif args[1] == "SurfaceTilt":  
                    if int(args[5]) == 0 and args[7] in ['YT', 'XT', 'ZT']:
                        cmdArgs = { 'c'     : int(args[2]),
                                    'n'     : int(args[3]) - 1,
                                    'a'     : float(args[4]),
                                    'axis'  : args[6]}
                        codeVsurfNum =  args[12]          
                        toSend = il.ChaSurTil(cmdArgs)
                        if int(args[8]) == 0 and args[9] in ['YT', 'XT', 'ZT']:
                            il.RemoveSurface(int(args[2]),int(args[3]) + 1)
                        if toSend == True:
                            toSend ="True"
                        else:
                            toSend ="False"    
                    else:
                        cmdArgs = { 'c'     : int(args[2]),
                                    'n'     : int(args[3]) - 1,
                                    'a'     : float(args[4]),
                                    'p'     : int(args[5]),
                                    'axis'  : args[6]}
                        codeVsurfNum =  args[12]            
                        toSend = il.SurfaceTilt(cmdArgs)
                        if toSend == True:
                            toSend ="True"
                        else:
                            toSend ="False"    
                    if (args[10] == "True"): 
                        il.BasicDecenterCodeV(codeVsurfNum,args[4],args[10],args[11])
                    else:
                        il.BasicDecenterCodeV(codeVsurfNum,args[4],args[10],"None")    
                    router.send_multipart([clientID, toSend.encode()])  
                elif args[1] == "ChangeZernike":
                    il.SetImageDistanceSolve(0,False)
                    l = " ".join(args[8:43])
                    l = l.split()
                    for i in range(0, len(l)):
                        l[i] = float(l[i])
                    cmdargs = { "codeVsurfaceNumber" : args[45],
                                "coefficients"       : l}   
                    il.ChangeZernikeCoefficients(args[46],cmdargs)             
                    cmdArgs = { "c"     : int(args[2]),
                                "p"     : int(args[3]),
                                "r"     : float(args[4]),
                                "dp"    : float(args[5]),
                                "dn"    : float(args[6]),
                                "su"    : float(args[7]),
                                "an"    : l,
                                "b"     : args[43],
                                "type"  : args[44]}
                    toSend = il.ChangeZernike(cmdArgs)
                    toSend = il.ChangeZernike(cmdArgs)
                    if toSend == True:
                        toSend ="True"
                    else:
                        toSend ="False"
                    il.Command("$eval")
                    router.send_multipart([clientID, toSend.encode()]) 
                elif args[1] == "ChangeTerm":
                    toSend = il.ChangeTerm(args[2],args[3],args[4])
                    router.send_multipart([clientID, toSend.encode()])                                                                                  
            else:
                router.send_multipart([clientID, ("Error: Unidentified command").encode()])
except KeyboardInterrupt:
    print("I don't feel so good...")
    cleanup()
    print("*DEAD*")
