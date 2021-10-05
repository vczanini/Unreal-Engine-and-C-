import os
import win32com.client
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy import cos as cos
from numpy import sin as sin
from numpy import deg2rad as d
from numpy import sqrt as s
from numpy import linspace as l

class FFD():
    def __init__(self):
        self.filename = None
        self.CodeV = None
        self.CodeVFlag = False
        self.FfdData = pd.DataFrame()
        self.Start = False
        self.isAngle = False
        self.Count = 0
        self.x = []
        self.y = []
        self.angle = []
        self.magnitude = []
        self.MaxMag = 0
        self.FieldSeparation = None
        self.SymbolX = None
        self.SymbolY = None
        self.xsym = None
        self.ysym = None
        self.XforPlot = None
        self.YforPlot = None

    def StartCodev(self):
        self.CodeV = win32com.client.gencache.EnsureDispatch("CodeV.Command")
        self.CodeV.SetStartingDirectory(os.getcwd())
        self.CodeV.StartCodeV() 
        self.CodeVFlag = True   

    def LoadOpticalSystem(self, filename):
        resp = self.CodeV.Command("in "+ filename).split(" ")[0].split(":")[0]
        if (resp != "Error"):
            resp = True
            return resp
        else:
            resp = False
            return resp
    

    def StopCodev(self):
        self.CodeV.StopCodeV()  

    def Initialize(self):
        self.FfdData = pd.DataFrame()
        self.Start = False
        self.isAngle = False
        self.Count = 0
        self.x = []
        self.y = []
        self.angle = []
        self.magnitude = []
        self.MaxMag = 0
        self.avgs = 0 
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None  
        self.FieldSeparation = None
        self.SymbolX = None
        self.SymbolY = None
        self.xsym = None
        self.ysym = None
        self.XforPlot = None
        self.YforPlot = None                 

    def PlotFFD(self,ffdScale,xangle,yangle,aberration):

        self.xmin = "-"+xangle
        self.xmax = xangle
        self.ymin = "-"+yangle
        self.ymax = yangle
        resp = None
        if ((aberration == "5") or (aberration == "6")):
            resp = self.CodeV.Command("FMA; FFD WPO; WPT ZFR 37; XMI "+self.xmin+" ; XMA "+self.xmax+" ; YMI "+self.ymin+" ; YMA "+self.ymax+" ; NFX 11 ; NFY 11 ; SSI 0 ; TGR 256; NRD 100; WCN 5;go")
            self.isAngle = True
            self.ParseData(resp,float(ffdScale))
            self.AstigmatismFFDSymbol()
            plt.title("Fringe Zernike Pair Z5 and Z6")
        elif ((aberration == "7") or (aberration == "8")):
            resp = self.CodeV.Command("FMA; FFD WPO; WPT ZFR 37; XMI "+self.xmin+" ; XMA "+self.xmax+" ; YMI "+self.ymin+" ; YMA "+self.ymax+" ; NFX 11 ; NFY 11 ; SSI 0 ; TGR 256; NRD 100; WCN 7;go")
            self.isAngle = True
            self.ParseData(resp,float(ffdScale))
            self.ComaFFDSymbol() 
            plt.title("Fringe Zernike Pair Z7 and Z8") 
        elif (aberration == "4"):
            resp = self.CodeV.Command("FMA; FFD WPO; WPT ZFR 37; XMI "+self.xmin+" ; XMA "+self.xmax+" ; YMI "+self.ymin+" ; YMA "+self.ymax+" ; NFX 11 ; NFY 11 ; SSI 0 ; TGR 256; NRD 100; WCN 4;go")      
            self.ParseData(resp,float(ffdScale))
            self.CirclePlot()
            plt.title("Fringe Zernike Term Z4")
        elif (aberration == "0"):
            resp = self.CodeV.Command("FMA;FFD RWE; XMI "+self.xmin+" ; XMA "+self.xmax+" ; YMI "+self.ymin+" ; YMA "+self.ymax+" ; NFX 11; NFY 11 ; SSI 0;go;")      
            self.ParseData(resp,float(ffdScale))
            self.CirclePlot() 
            plt.title("RMS Wavefront Error")               
        if(resp != None):
            resp = self.SavePlot()           
            return resp
        else:
            resp = "No such aberration exists"
            return resp    
        

    def ParseData(self, resp,ffdscale):
        resp = resp.split("\r\n")
        for line in resp:
            if(line != ''):
                line = line.split()
                if (line[0] == "X-Field"):
                    self.Start = True
                    continue
                if (line[0] == "FIELD" or self.Count == 121):
                    self.Start = False                
                if ((self.Start == True) and (self.Count < 121)):
                    self.x.append(float(line[0]))
                    self.y.append(float(line[1]))
                    self.magnitude.append(float(line[2]))
                    if (self.isAngle):
                        self.angle.append(float(line[3]))
                    self.Count = self.Count + 1
                if (line[0] == "Average"):
                    self.avgs = float(line[3])    


        self.FfdData['X-Field'] = self.x
        self.FfdData['Y-Field'] = self.y
        self.FfdData['Magnitude'] = self.magnitude
        if (self.isAngle):
            self.FfdData['Angle'] = self.angle
        self.MaxMag = max(self.magnitude)/ffdscale
        a=(2*max(self.x))/10
        b=(2*max(self.y))/10
        self.FieldSeparation = min(a, b)

    def SavePlot(self):

        textstring = 'Maximum value=%.2f\nMinmum value=%.2f\nAverage value=%.2f\n'%(float(max(self.magnitude)),float(min(self.magnitude)),self.avgs)
        plt.gcf().text(0.02,0.5,textstring,fontsize = 10)
        plt.subplots_adjust(left = 0.3)
        plt.savefig(os.getcwd() + '\\Examples\\Unity\\PC+Mobile (2D)\\demo\\Assets\\StreamingAssets\\FFD.png')
        plt.clf()
        self.Initialize()
        resp = "The FFD was plotted"
        return resp

    def ComaFFDSymbol(self):

        self.SymbolX = [cos(d(-30)),0.0,cos(d(30))]/(3/s(3))
        self.xsym =((1/s(3))*cos(d(l(-270,-270+360,101)))+(2/s(3)))/(3/s(3))
        self.SymbolX = np.concatenate((self.SymbolX,self.xsym))
        self.SymbolY = [sin(d(-30)),0.0,sin(d(30))]/(3/s(3))
        self.ysym =((1/s(3))*sin(d(l(-270,-270+360,101))))/(3/s(3))
        self.SymbolY= np.concatenate((self.SymbolY,self.ysym))
        for i in range(len(self.FfdData)):
            orientation = (-1)*(d(self.FfdData['Angle'][i]))
            self.XforPlot = self.SymbolX*cos(orientation) + self.SymbolY*sin(orientation)
            self.YforPlot = -1*self.SymbolX*sin(orientation) + self.SymbolY*cos(orientation)
            plt.plot(self.FfdData['Magnitude'][i]*self.XforPlot*(self.FieldSeparation/self.MaxMag)+self.FfdData['X-Field'][i],self.FfdData['Magnitude'][i]*self.YforPlot*(self.FieldSeparation/self.MaxMag)+self.FfdData['Y-Field'][i],color = 'black')        

    def AstigmatismFFDSymbol(self):

        self.SymbolX = [0.0,0.0]/(1/s(1))
        self.SymbolY = [-0.5,0.5]/(1/s(1))  
        for i in range(len(self.FfdData)):
            orientation = (-1)*(d(self.FfdData['Angle'][i]))
            self.XforPlot = self.SymbolX*sin(orientation) + self.SymbolY*cos(orientation)
            self.YforPlot = self.SymbolX*cos(orientation) - self.SymbolY*sin(orientation)
            plt.plot(self.FfdData['Magnitude'][i]*self.XforPlot*(self.FieldSeparation/self.MaxMag)+self.FfdData['X-Field'][i],self.FfdData['Magnitude'][i]*self.YforPlot*(self.FieldSeparation/self.MaxMag)+self.FfdData['Y-Field'][i],color = 'black')

    def CirclePlot(self):
        
        for i in range(len(self.FfdData)):
            plt.plot(self.FfdData['X-Field'][i],self.FfdData['Y-Field'][i],marker = 'o',ms = abs(self.FfdData['Magnitude'][i]/self.MaxMag) * 10, mec = 'k', mfc = 'w')

    def DecenterAndBend(self, surfaceNumber):
        resp = self.CodeV.Command("BEN S" + surfaceNumber)    

    def DecenterAndReturn(self, surfaceNumber):
        resp = self.CodeV.Command("DAR S" + surfaceNumber)        

    def BasicDecenter(self, surfaceNumber, isTilted, tiltType):
        if (isTilted == "True" and tiltType != "BAS"):
            resp = self.CodeV.Command("DEL " + tiltType + " S" + surfaceNumber)
        else:
            resp = self.CodeV.Command("XDE S" + surfaceNumber +" (XDE S" + surfaceNumber + ")")   

    def AddAlphaTilt(self, surfaceNumber, angle):
        resp = self.CodeV.Command("ADE S" + surfaceNumber + " " + angle) 

    def ChangeSurfaceToZernike(self, surfaceNumber):
        resp = self.CodeV.Command("SPS ZFR S" + surfaceNumber)

    def SetZernikeCoefficients(self,args):
        codeVsurfaceNumber = args['codeVsurfaceNumber']
        zernikeCoefficients = args['coefficients']
        for i in range(len(zernikeCoefficients)):
            resp = self.CodeV.Command("SCO S" + codeVsurfaceNumber+ " C" + str(i + 4) + " " + str(zernikeCoefficients[i]))

    def SetZernikeTerm(self,surfaceNumber,zerniketerm,zernikevalue):
        resp = self.CodeV.Command("SCO S" + surfaceNumber+ " C" + str(zerniketerm + 3) + " " + zernikevalue)
        if(resp != None):
            resp = "True"           
            return resp
        else:
            resp = "False"
            return resp 

if __name__ == "__main__":
    pass