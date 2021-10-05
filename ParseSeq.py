import os
import codev
import math

class SeqObject():
    
    def __init__(self, interface):
        self.Interface = interface
        self.filename = None
        self.OpticalModel = codev.OpticalModel()

    def ReadSeq(self, filename):
        """return true if .seq file exists"""

        self.filename = filename
        self.OpticalModel = codev.read_seq(filename)
        if self.OpticalModel.file_name == None:
            return False
        return True

    def InsertSurfaces(self):
        """ insert all surfaces in the list"""
        # make sure the aperture stop and tilt/decenter surfaces are dummy surfaces
        self.OpticalModel.split_surfaces()
        surfaces = self.OpticalModel.surfaces
        surf0_gap = surfaces[0].gap
        if surf0_gap >= 10**9:
            self.Interface.ChangeReferenceSurface({'c':0,'dn':0,'gl':'AIR'})
            # set the first surface at the reference position
            dis_p = 0
        else:
            # finite conjugate system
            self.Interface.ChangeSystemClass(0, 'CRL')
            self.Interface.SetObjectDistance(-2) # set Object positon at the referece surface
            self.Interface.ChangeReferenceSurface({'c':0,'dn':surfaces[0].gap,'gl':'AIR'})
            dis_p = surf0_gap

        # Remove the aperture stop, new stop will be inserted later
        self.Interface.RemoveSurface(0, 1) 
        # Add all surfaces in surface list
        for ind, surface in enumerate(surfaces):
            if surface.name == "SO": #skip object plane
                continue
                
            if ind != 1: 
                dis_p = surfaces[ind-1].gap

            if surface.is_aperture_stop: # Aperture Stop
                self.Interface.InsertApertureStop({
                                                'c': 0, 
                                                's': ind-1,
                                                'dp': dis_p,
                                                'dn': surface.gap
                                                })
                continue

            if surface.decenter_dict['type'] == 'Basic':
                self._DecenterAndTilt(surface, dis_p)
                continue

            if surface.isReflective():
                surf_type = "reflective"
            else:
                surf_type = "refractive"

            if surface.curvature == 0:
                radius = "INF"
            else:
                radius = 1 / surface.curvature

            surf_dict = {
                        'c': 0,   #configration number
                        's': ind-1, # insert after surface #
                        'r': radius,
                        'dp': dis_p,
                        'dn': surface.gap,
                        'gl': self._GetGlassName(surface.glass),
                        'type': surf_type
                        }    

            if surface.nradius != 0:
                surf_dict['p'] = surf_dict['s']
                del surf_dict['s']
                surf_dict['b'] = surf_dict['gl']
                del surf_dict['gl']
                surf_dict['su'] = surface.nradius
                surf_dict['an'] = surface.zfr_coef[:35]

            # insert surfaces
            if surface.name == "SI":
                surf_dict['s'] = ind
                del surf_dict['type']
                response = self.Interface.ChangeRefractiveSurface(surf_dict)
            elif len(surf_dict) > 7:
                response = self.Interface.InsertZernike(surf_dict)
            else:
                response = self.Interface.InsertSurface(surf_dict)

            if not response:
                print('Fail to add S ' + ind)
                return False

        return True

    def _DecenterAndTilt(self, surface, dis_p):
        axes = {'tilt':{'ADE':'y', 'BDE':'z', 'CDE':'x'},
                'decenter': {'XDE':'z', 'YDE':'y', 'ZDE':'x'}}
        d_dict = surface.decenter_dict
        for key in axes['decenter']:
            if key in d_dict and d_dict[key]:
                axis = axes['decenter'][key]
                d = - d_dict[key] if axis == 'z' else d_dict[key]
                self.Interface.SurfaceMove({
                                    'c': 0,
                                    'n': surface.ind-1,
                                    'd': d,
                                    'axis': axis
                })

        for key in axes['tilt']:
            if key in d_dict and d_dict[key]:
                axis = axes['tilt'][key]
                a = -d_dict[key] if axis == 'z' else d_dict[key]
                zod = d_dict.get('ZOD', 0) # x axis (in Eikonal) tilt offset
                self.Interface.SurfaceTilt({
                                    'c': 0,
                                    'n': surface.ind-1,
                                    'a': a,
                                    'p': dis_p+zod,
                                    'axis': axis
                })

    def SetFields(self, field_type, fields):
        """Set field of view and add field points"""

        if field_type == 'ANG': #Object Angle, use HFOV
            half_angle_x = max(map(abs, fields['XAN']))
            half_angle_y = max(map(abs, fields['YAN']))
            if half_angle_x != 0:
                self.Interface.SetAberrationSymmetry(0, 'ASYM')
                self.Interface.SetRotationalSymmetry(0, 'NRS')
                self.Interface.SetObjectAngle(half_angle_x,'E')
            self.Interface.SetObjectAngle(half_angle_y)

            for ind, y_ang in enumerate(fields['YAN']):
                # z = -x(in codev) 
                z_ang = -fields['XAN'][ind]
                if y_ang != 0 or z_ang != 0: 
                    self.Interface.InsertFieldPoint("HFOV",0 ,y_ang, z_ang) ##configration number =0

        elif field_type == 'IMG': #Image height, use FIH
            image_height_x = max(map(abs, fields['XIM']))
            image_height_y = max(map(abs, fields['YIM']))
            if image_height_x != 0:
                self.Interface.SetAberrationSymmetry(0, 'ASYM')
                self.Interface.SetRotationalSymmetry(0, 'NRS')
                self.Interface.SetImageHeight(image_height_x,'E')
            self.Interface.SetImageHeight(image_height_y)

            for ind, y_ima in enumerate(fields['YIM']):
                z_ima = -fields['XIM'][ind]
                if y_ima !=0 or z_ima != 0:
                    try:
                        y_fih = y_ima / image_height_y
                    except ZeroDivisionError :
                        y_fih = 0
                    try:
                        z_fih = z_ima / image_height_x
                    except ZeroDivisionError:
                        z_fih = 0

                    self.Interface.InsertFieldPoint("FIH", 0, y_fih, z_fih)

    def ParseSeq(self,filename):
        """ This function parses the seq file and saves the lens in a .A file"""
        resp = self.ReadSeq(filename)

        if not resp:
            print("{} does not exist.".format(filename))
            return

        # Load the initial lens
        self.Interface.LoadSystem('InitLens.A')

        self.Interface.Command("$EVAL")
        # set wavelengths
        wl = sorted(self.OpticalModel.wavelengths)

        while len(wl) < 3:
            wl.append(wl[-1])

        self.Interface.SetWavelengths(0, [wl[1]/1000, wl[0]/1000, wl[2]/1000])

        # Insert Surfaces    
        self.InsertSurfaces()

        # Set pupil size
        self.Interface.SetImaFNumber(self.OpticalModel.fno)

        # Set Fields
        self.SetFields(self.OpticalModel.field_type,self.OpticalModel.fields)

        # Paraxiel image solve
        self.Interface.SetImageDistanceSolve(0, self.OpticalModel.paraxial_image_solve)

        #eval
        self.Interface.Command("$EVAL")

        #Vifa
        self.Interface.Command("$VIFA")

        # resp = self.getSurfaceDataTable()
        # print(resp)

        response = self.Interface.SaveSystem(filename)

        return response

    def WriteSeq(self, filename):
        
        self.filename = (os.path.splitext(filename)[0] + '_test.seq').strip("\"\'")
        if os.path.exists(self.filename):
            print(self.filename + " already exists.")
            return
        
        self.Interface.LoadSystem(filename)

        self.Interface.Command("$eval")

        surface_list = self.Interface.GetSurfaces(0)
        img_dis_sol = self.Interface.GetGeneralSystemSettings(0)['ImageDistanceSol']
        sys_type_m = self.Interface.GetGeneralSystemSettings(0)['SystemType (M)'] 
        sys_sym = self.Interface.GetGeneralSystemSettings(0)['RotationalSym']
        f_number =  self.Interface.GetFNumber(0)
        name = self.Interface.GetName(0)
        unit = self.Interface.GetUnit(0)
        img_height_y = self.Interface.GetImageHeight(0)

        if sys_sym != 'RotationallySymmetric': 
            img_height_x = self.Interface.GetImageHeight(0, 'E')
        else:
            img_height_x = img_height_y
        
        wls = sorted(self.Interface.GetWavelengths(0),reverse=True)
        wls_nm = [wl*1000 for wl in wls]
        fractional_heights = self.Interface.ListFieldPoints(0)

        wls_str = '{}'.format(wls_nm).strip('[]').replace('\'','').replace(',','')
        y_height = [img_height_y * frac_height[0] for frac_height in fractional_heights]
        x_height = [-img_height_x * frac_height[1] for frac_height in fractional_heights]
        y_height_str = '{}'.format(y_height).strip('[]').replace('\'','').replace(',','')
        x_height_str = '{}'.format(x_height).strip('[]').replace('\'','').replace(',','')

        with open(self.filename, 'w') as writer:
            # System data: 
            writer.writelines(['RDM NO; LEN\n',
                               'TITLE "{}"\n'.format(name),
                               'DIM {}\n'.format(unit[0].upper()),
                               'FNO {}\n'.format(f_number),
                               'WL {}\n'.format(wls_str),
                               'YIM {}\n'.format(y_height_str),
                               'XIM {}\n'.format(x_height_str),
                               ])

            if sys_type_m == 'Objective':
                writer.write('SO 0.0 1e+13\n') #object at infinity
            elif sys_type_m == 'CommonRelay':
                obj_distance = self.Interface.GetObjectDistance(0)
                writer.write('SO 0.0 {}\n'.format(-obj_distance))

            for ind, surf in enumerate(surface_list):
                typenumber = surf['typeNumber']

                if typenumber not in (3,4): # ignore reference/object/image surface
                    continue
                
                typecode = surf['TypeCode']
                curvature = surf['Curvature']
                dist_to_next = surf['DistToNext']
                glass = surf['GlassName'] if surf['GlassName'] != None else ''

                # sign of RefrIndex changes when it is a reflective surface
                if surf['RefrIndex'] * surface_list[ind-1]['RefrIndex'] < 0:
                    glass = 'REFL'
                
                if typecode in ['SP', 'AS', 'ZR']:
                    # todo private catalog glass 
                    writer.write('S {} {} {}\n'.format(curvature, dist_to_next, glass))

                if typecode == 'ZR':
                    # TODO get zernike coefs and nradius from backend
                    pass
                
                if typecode == 'AS':
                    writer.write('STO\n')

                elif typecode == 'ZD':
                    writer.writelines(['S 0.0 {} {}\n'.format(dist_to_next, glass),
                                       '  XDE {}\n'.format(-curvature)])
                elif typecode == 'YD':
                    writer.writelines(['S 0.0 {} {}\n'.format(dist_to_next, glass),
                                       '  YDE {}\n'.format(curvature)])
                elif typecode == 'XD':
                    writer.writelines(['S 0.0 {} {}\n'.format(dist_to_next, glass),
                                       '  ZDE {}\n'.format(curvature)])
                elif typecode == 'ZT':
                    writer.writelines(['S 0.0 {} {}\n'.format(dist_to_next, glass),
                                       '  BDE {}\n'.format(-curvature*180/math.pi)])
                elif typecode == 'YT':
                    writer.writelines(['S 0.0 {} {}\n'.format(dist_to_next, glass),
                                       '  ADE {}\n'.format(curvature*180/math.pi)])
                elif typecode == 'XT':
                    writer.writelines(['S 0.0 {} {}\n'.format(dist_to_next, glass),
                                       '  CDE {}\n'.format(curvature*180/math.pi)])

                if ind == len(surface_list)-2 and img_dis_sol == 'On':
                    writer.write('PIM\n')

            writer.write('SI 0.0 0.0\n')
            
    def _GetGlassName(self,glass):
        """ get glass name in eikonal backend
        """
        catalog = ''
        gl = glass.upper().split('_') 
        gl_name = gl[0] or 'AIR'
        if len(gl) > 1:
            catalog = gl[1]
        if catalog == 'OHARA':
            if gl_name[0] == 'S':
                gl_name = gl_name[0] + "-" + gl_name[1:]
            else:
                gl_name = "-" + gl_name
        
        return gl_name            



if __name__ == "__main__":
    # test ParseSeq in main
    pass