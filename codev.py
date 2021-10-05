# code v reader inspired by Michael J. Hayford (rayoptics)
# adopted with some modification to make it working on generic case


import logging
from typing import List
import text_reader
import numpy as np
import os

class Surface:
    ''' container for surface defined in code v sequence file
    It is caller's responsibility to convert this into useful object.
    
    '''
    def __init__(self):
        self.type='SPH'
        self.name=''
        self.label=''  # user supplied label
        self.curvature=0.0 #1/R
        self.gap=0.0  # per code v, gap after surface
        self.glass='' # when empty, use air
        self.k=0.0 # conic constant
        self.asp_coef=np.zeros(9).tolist() # asphere coefficients
        self.nradius=0.0 # zernike normalize radius
        self.zfr_coef=np.zeros(37).tolist() # ZFR, fringe coef
        self.aperture={} # aperture definition, dictionary, last same key wins
        self.clear_aperture={}
        self.mirror_back_curvature=0.0 # first surface mirror back curvature
        self.mirror_thickness=0.0  # first surface mirror thickness
        self.ind=0  # surface index, start from 1
        self.is_aperture_stop = False # 
        self.decenter_dict = {'type': None} # decenter type of the surface

        self.file_name=None
        
    def isReflective(self):
        if self.glass=='REFL':
            return True
        else:
            return False     
        
    def getSurfaceName(self):
        ''' return surface name in system with incremental index. For single 
        surface, it is 'S'; for named surface, it is 'SI, SO, SL'; for 
        auto-indexed surface, it is 'S1, S2, S3, ...'
        '''
        
        if self.name in ('SI', 'SO', 'SL'):
            name = self.name
        elif self.ind>0:
            name='S'+str(self.ind).zfill(3)

            
        if self.label:
            # name=name+'('+self.label+')'
            name=self.label
        return name
    
    def get_aperture(self, ca=False):
        ''' return the aperture dict '''
        
        if ca:
            aperture = self.clear_aperture
        else:
            aperture = self.aperture
          
        my_aperture = {}
        
        a=0
        b=0
        wx=0
        wy=0
        for k in aperture.keys():
            atype,value=aperture[k]
            # print(atype, value)

            if k == 'CIR':
                my_aperture['type']='circle'
                my_aperture['parameter']=[value]
            elif k=='ELX':
                my_aperture['type']='ellipse'
                a=value
                my_aperture['parameter']=[a,b]
            elif k=='ELY':
                my_aperture['type']='ellipse'
                b=value
                my_aperture['parameter']=[a,b]
            elif k=='REX':
                my_aperture['type']='rectangle'
                wx=value
                my_aperture['parameter']=[wx,wy]
            elif k=='REY':
                my_aperture['type']='rectangle'
                wy=value
                my_aperture['parameter']=[wx,wy]
                
        
        # check validness of each
        if my_aperture!={}:
            for i in my_aperture['parameter']:
                if i<=0:
                    aperture=None
        else:
            my_aperture=None
    
                
        return my_aperture
        
    def is_dummy(self, prev_surf):
        if self.name in ["SO", "SI"]:
            return False

        if prev_surf.isReflective():
            
            return (not self.glass) or self.glass == 'air'

        return not self.isReflective() and self.has_same_glass(prev_surf)


    def has_same_glass(self, other):
        if (not self.glass or self.glass.lower() == 'air') and \
            (not other.glass or other.glass.lower() == 'air'):
                return True

        return self.glass.lower() == other.glass.lower()


    def print_data(self):
        name=self.getSurfaceName()
        glass=self.glass
        if not glass:
            glass='air'
        
        print(*[name,self.type,self.curvature,self.gap,glass], sep=', ')
     
        
class DecenterSurface(Surface):
    ''' container for dummy surface created for surface tilt and decenter.

    '''
    def __init__(self,decenter_dict, ind=0):
        super().__init__()
        self.decenter_dict = decenter_dict
        self.gap = 0
        self.ind = ind
        self.glass = "air"
        self.name = "S"
        self.is_aperture_stop = False
        self.type = self.get_decenter_type()

    def get_decenter_type(self):
        for i, key in enumerate(CV_DECENTER[:6]):
            if key in self.decenter_dict and self.decenter_dict[key]!=0:
                return "TILT" if i >= 3 else "DECENTER"

    def print_data(self):
        name='S'+str(self.ind).zfill(3)
        glass=self.glass
        if not glass:
            glass='air'
        
        print(*[name,self.type,0,self.gap,glass], sep=', ')
    
class OpticalModel:
    ''' container for store code v optical model information. 
    It is caller's responsibility to convert this into something used for calculation.
    
    '''
    
    def __init__(self,radius_mode=False):
        self.radius_mode = radius_mode
        self.title = ''
        self.author = ''
        self.unit = 'M'
        self.unit_scale = 1.0 # default to mm
        self.epd = 0.0
        self.fno = 0.0
        self.s_ind = 0 # current surface index, start from 1
        self.as_ind = 0 # index of aperture stop

        self.surfaces = [] # surface object as imported
        self.lens = [] # created element based on knowledge of code
        self.mirror = []

        self.surface_ind=dict() # surface name dict

        self.fields = dict()
        self.field_type = ''
        self.field_w = list()

        self.wavelengths = list()
        self.ref_wavelength = 0.0
        self.wavelength_w = list()

        self.private_gl = list()  
        self.file_name=None  # file name to code v file
        self.paraxial_image_solve = False

        
    def add_surface(self, s):
        
        if s.name=='S':
            self.s_ind+=1  
            s_name='S'+str(self.s_ind)
        elif s.name == 'SI':
            self.s_ind+=1
            s_name = s.name
        else:
            s_name=s.name
        s.ind=self.s_ind
        self.surface_ind[s_name]=s
        self.surfaces.append(s)
        
    def find_element(self):
        ''' find elements from the surface list. '''

        num=len(self.surfaces)
        for ind, s in enumerate(self.surfaces):
            
            if s.isReflective():
                self.mirror.append(s)    
                continue
                
            if s.glass and ind<num-1:
                self.lens.append(s)
                self.lens.append(self.surfaces[ind+1])
                
            

                
                # find glass material with thickness
                # make that as lens
                
                # find reflective surface; if the last one is not glass
                # make it as mirror


    def split_surfaces(self):
        ''' seperate aperture stop and decenter/tilt from optical surfaces 
            convert BEN/DAR type surfaces into Basic type surfaces
        '''
        new_surf_list = []
        for ind, s in enumerate(self.surfaces):
            if s.decenter_dict["type"] != None:
                self._split_decentered_surface(s, s.decenter_dict["type"], new_surf_list)
            elif s.is_aperture_stop and not s.is_dummy(new_surf_list[-1]):
                self._split_as_surface(s, new_surf_list)                   
            else:
                new_surf_list.append(s)

        for i, s in enumerate(new_surf_list):
            s.ind = i
        
        self.surfaces = new_surf_list

    def _split_decentered_surface(self, s, dtype, new_surf_list):
        surfaces_front = []
        surfaces_back = []
        for i, cmd in enumerate(CV_DECENTER[:6]):  
            if s.decenter_dict[cmd]:   
                new_surf = DecenterSurface({'type':'Basic', cmd:s.decenter_dict[cmd]})
                surfaces_front.append(new_surf)
                if dtype == 'BEN' and i >= 3 :
                    new_surf_back = DecenterSurface({'type':'Basic', cmd:s.decenter_dict[cmd]})
                    surfaces_back.insert(0,new_surf_back)
                elif dtype == 'DAR' and s.name == "S":
                    new_surf_back = DecenterSurface({'type':'Basic', cmd:-s.decenter_dict[cmd]})
                    surfaces_back.insert(0,new_surf_back)
        
        for i, surf in enumerate(surfaces_front):
            tilt_keys = ('ADE', 'BDE', 'CDE')
            if any(cmd in surf.decenter_dict for cmd in tilt_keys)  :
                surf.decenter_dict['ZOD'] = s.decenter_dict['ZOD']
                if i > 0:
                    surfaces_front[i-1].gap = new_surf_list[-1].gap
                    new_surf_list[-1].gap = 0
                break

        if len(surfaces_front) > 0:
            surfaces_front[-1].gap = -s.decenter_dict['ZOD']
        if len(surfaces_back) > 0:
            surfaces_back[-1].gap, s.gap = s.gap - s.decenter_dict['ZOD'], 0
            surfaces_back[0].decenter_dict['ZOD'] = s.decenter_dict['ZOD']
        
        s.decenter_dict = {'type': None}

        if s.is_dummy(new_surf_list[-1]) and not s.is_aperture_stop:
            if surfaces_back == []:
                surfaces_front[-1].gap += s.gap
            new_surf_list.extend(surfaces_front+surfaces_back)
        else:
            new_surf_list.extend(surfaces_front+[s]+surfaces_back)

    def _split_as_surface(self, s, new_surf_list):
        new_as = Surface()
        new_as.is_aperture_stop = True
        new_as.file_name = s.file_name
        new_as.name = "S"
        s.is_aperture_stop = False
        if (not s.glass) or s.glass.lower() == 'air': # glass-air 
            new_as.gap, s.gap = s.gap, 0
            new_surf_list.extend([s,new_as])
        else: # air-glass
            new_as.gap = 0 
            new_surf_list.extend([new_as,s])      

    def print_data(self):
        print()
        print(self.title)
        print('Sk, Type, Curvature, Gap, Glass')
        for s in self.surfaces:
            s.print_data()
        
        ind=1
        for s in self.mirror:
            if ind==1:
                print()
            print('M '+str(ind).zfill(2)+':')
            s.print_data()
            ind+=1
            
        print()
        num=len(self.lens)
        ind=1
        for i in range(0,num,2):
            if ind==1:
                print()
            print('Lens '+str(ind).zfill(2)+':')
            self.lens[i].print_data()
            self.lens[i+1].print_data()
            ind+=1

            
        
# system level command
CV_CMD=['RDM','TITLE','EPD','FNO','NA','DIM','WL','RFE','WTW','INI',
        'XAN','YAN','XIM','YIM','XOB','YOB','XAN','YAN','WTF',
        'VUX','VLX','VUY','VLY',
        'GO','PIK','CLS','DER','LEN','REF','TEM']

def cv_cmd(opm, c):
    ''' process code v commands '''
    # 
    cmd=c[0].upper()
    q=c[1:]
    if cmd=='RDM':
        if len(q) == 0:
            opm.radius_mode = True
        elif q[0].upper() != 'N' and q[0].upper() != 'NO':
            opm.radius_mode = True
    elif cmd=='TITLE':
        opm.title=q[0]
    elif cmd=='EPD':  #TODO convert EPD to FNO, need focla length
        opm.epd=float(q[0])
        # if no aperture is provided, this is used as default aperture
    elif cmd == 'FNO':
        opm.fno=float(q[0])
    elif cmd == 'NA':
        opm.fno=1/2/float(q[0])
    elif cmd=='DIM':
        opm.unit=q[0]
        if opm.unit=='C':
            opm.unit_scale=10.0
        elif opm.unit=='I':
            opm.unit_scale=25.4
        elif opm.unit=='M':
            opm.unit_scale=1.0
        else:
            logging.error("not recorgnized unit: %s", c) 
    ## commands for Field Specification:
    elif cmd == 'XIM' or cmd == 'YIM': # Paraxial image height
        opm.field_type = 'IMG'
        opm.fields[cmd] = list(map(float,q))
    elif cmd == 'XAN' or cmd == 'YAN': # Object ANgle
        opm.field_type = 'ANG'
        opm.fields[cmd] = list(map(float,q))
    elif cmd == 'XOB' or cmd == 'YOB': # Object Height
        opm.field_type = 'OBJ'
        opm.fields[cmd] = list(map(float,q))
    elif cmd == 'XRI' or cmd == 'YRI': # Real Image Height
        opm.field_type = 'RIH'
        opm.fields[cmd] = list(map(float,q))
    elif cmd == 'WTF':
        opm.field_w = list(map(float,q))   

    ## commands for Wavelength Specifivcaion:
    elif cmd == 'WL':
        opm.wavelengths = list(map(float,q))
    elif cmd == 'REF':
        opm.ref_wavelength = opm.wavelengths[int(q[0])-1]
    elif cmd == 'WTW':
        opm.wavelength_w = list(map(float,q))

# surface commands
CV_SURFACE=['CON','ASP','K', 
            'XDE','YDE','ZDE','ADC','BDC','CDC',
            'ADE','BDE','CDE','XOD','YOD','ZOD',
            'SPS','SCO','SCC', 
            'SLB','STO','PIM','BEN','CUM','THM','THC','CCY','DAR','RET','REV',       
            'CIR','ELX','ELY','REX','REY',
            'A','B','C','D','E','F','G','H','J',
            'ADX', 'CUF']   
CV_DECENTER=['XDE', 'YDE', 'ZDE', 'ADE', 'BDE', 'CDE', 'XOD', 'YOD', 'ZOD']
ASP_COEF=['A','B','C','D','E','F','G','H','J']
 
def cv_surface_cmd(opm: OpticalModel, c: List[str]):
    ''' process code v surface commands '''
    cmd=c[0].upper()
    
    s=opm.surfaces[-1]
    
    if cmd in ['CON','ASP'] :
        s.type=cmd
    elif cmd=='K':
        s.k=float(c[1])
    elif cmd=='SLB':
        s.label=c[1]
    elif cmd =='SPS':
        s.type=c[1].upper()
    elif cmd in ASP_COEF:
        i=ASP_COEF.index(cmd)
        q=float(c[1])
        s.asp_coef[i]=q
    elif cmd == 'SCO':
        q=c[1].upper()
        if q == 'K':
            s.k=float(c[2])
        elif q == 'NRADIUS':
            s.nradius=float(c[2])
        elif q[1::].isnumeric():
            ind=int(q[1::])-4
            if ind>=0 and ind<=36:
                s.zfr_coef[ind]=float(c[2])
            else:
                logging.error("not supported: %s", c)
        else:
            logging.error("not supported: %s", c)
    elif cmd in ['CIR','ELX','ELY','REX','REY']:
        if len(c) == 2:
            s.clear_aperture[cmd]=['CLR',float(c[1])]
        else:
            s.aperture[cmd]=[c[1].upper(), float(c[2])]
    elif cmd == 'CUM':
        s.mirror_back_curvature=float(c[1])
    elif cmd == 'THM':
        s.mirror_thickness=float(c[1])
    elif cmd == 'STO':
        s.is_aperture_stop = True
        opm.as_ind = s.ind
    elif cmd == 'PIM':
        opm.paraxial_image_solve = True
    elif cmd in ['BEN', 'DAR', 'REV']:
        # dencenter types: decenter and bend, decenter and return, reverse decenter
        s.decenter_dict['type'] = cmd
    elif cmd == 'RET':
        # return to pior surface
        s.decenter_dict['type'] = cmd
        s.decenter_dict['return_surf'] = int(c[1].upper().replace('S',''))
    elif cmd in CV_DECENTER:
        s.decenter_dict[cmd] = float(c[1])
        s.decenter_dict['type'] = s.decenter_dict['type'] or 'Basic'
    if s.decenter_dict['type'] != None:
        for cmd in  CV_DECENTER:
            if not cmd in s.decenter_dict:
                s.decenter_dict[cmd] = 0.0

    
def cv_create_surface(opm, c):
    ''' create new surface '''
    cmd=c[0].upper()
    q=c[1:]
    
    if cmd[0]=='S':
        s=Surface()
        s.name=cmd
        if opm.radius_mode:
            r=float(q[0])
            if r!=0.0:
                s.curvature=1.0/r
        else:
            s.curvature=float(q[0])
        s.gap=float(q[1])
        if len(q)==3:
            gtype=q[2].upper()
            s.glass=gtype
            
        opm.add_surface(s)
                
            


def read_seq(filename):
    ''' given a CODE V .seq filename, process the file  '''
    
    logging.basicConfig(filename='error.log',
                        filemode='w',
                        level=logging.ERROR)
    opm=OpticalModel()
    
    try:
        lines=text_reader.text_to_lines(filename,
                        comment='!',
                        line_continue='&',
                        line_end=';')
        opm.file_name = os.path.basename(filename)
    except:
        return opm
    
    cmds=text_reader.tokenize_lines(lines,r"[^'\"\s]\S*|\".+?\"|'.+?'")
    # print(*cmds, sep='\n')
    

    
    in_surface=False
    in_prv=False
    
    for c in cmds:
        if c[0].upper() == 'PRV':
            in_prv=True
            continue
        elif in_prv and c[0].upper()=='END':
            in_prv=False
            continue
        elif in_prv:
            continue
            
        if in_surface and c[0].upper() in CV_SURFACE:             
            cv_surface_cmd(opm, c)        
        
        elif c[0][0].upper()=='S':
            cv_create_surface(opm, c)
            in_surface=True
        elif c[0].upper() in CV_CMD:
            in_surface=False
            cv_cmd(opm, c)
        else:
            logging.error("not supported: %s", c)


    
    return opm




if __name__ == "__main__":
    
    import re
    import pprint

    # from EikonalInterfaceLayer import Interface as eil
    
    # il = eil(True)
    # opt=read_seq('../tests/private-seq-files/fabtools_test_elliptical_rect_superconic.seq')
    model = read_seq('testing/ag_triplet.seq')
    model.print_data()
    for s in model.surfaces:
        print("S#{} {} Thinkness:{} Decenter:{}".format(s.ind, s.name, s.gap, s.decenter_dict))
    model.split_surfaces()
    model.print_data()
    for s in model.surfaces:
        print("S#{} {} Thinkness:{} Decenter:{}".format(s.ind, s.name, s.gap, s.decenter_dict))