#'XBeach Diagnostic Test Model Generator'
# Making bathymetry profiles

#%%GENERAL#####################################################################

import numpy as np
from xbeachtools import XBeachBathymetry
import logging

logger = logging.getLogger(__name__)
logger.info('bathy.py is called for')

#%%BATHYMETRY CLASS CONTAINING ALL BUILDING BLOCKS AND PROFILES################

class Bathymetry(XBeachBathymetry):  
    def __init__(self, dx= 1, dy= 1, width= 100, dunewidth=25, shorewidth= 75, length= 0, height= 0, slope = 1, duneslope= 1, D50= 200e-6, m= 0.67, s= 1.6, v= 1e-6, **kwargs):  
    
        self.x = None 
        self.y = None 
        self.z = None 
        
        self.dx = dx
        self.dy = dy
        self.width = width
        self.dunewidth = dunewidth
        self.shorewidth = shorewidth
        self.length = length
        self.height = height
        self.slope = slope
        self.duneslope = duneslope
        self.D50 = D50
        self.m = m
        self.s = s
        self.v = v        
    
### GENERAL BUILDING BLOCKS###
    def fall_velocity_vanrijn2007(self, temp = 15): #based on OET: dean_beach_profile.m
        logger.debug('Fall velocity according to Van Rijn 2007 is called for')    
        # Fall velocity according to Van Rijn 2007
        dss = self.D50
        rhoint=1024
        rhosol=2650
        dsand=0.000064
        dgravel=0.002
        ag=9.81
        s = rhosol / rhoint
        vcmol = 4.0e-5 / (20.0 + temp)  
        if dss < 1.5*dsand:
            ws = (s-1.0) * ag * dss^2/(18.0*vcmol)
        elif dss < 0.5*dgravel:
            if dss < 2.0*dsand:
                coefw = (-2.9912/dsand) * dss + 15.9824
            else:
                coefw = 10.0            
            ws = coefw * vcmol / dss * (np.sqrt(1.0 + (s-1.0)*ag*dss**3 / (100.0*vcmol**2)) - 1.0)
        else:
            ws = 1.1 * np.sqrt((s-1.0)*ag*dss)
        logger.debug('ws= ', str(ws))
        return ws
           
    def dean1(self, zmin, zmax, beta_dry, height = 0):        #based on OET: dean_beach_profile.m (not exactly the same)
        logger.info('dean profile 1 is called for')        #beta_dry is the dry slope (above z=0)
        x = np.arange(-10000, 10000, self.dx)
        vfall = self.fall_velocity_vanrijn2007()
        logger.debug('vfall= ', str(vfall))
        a = 0.51 * vfall ** 0.44
        z = -a*np.power(abs(x), self.m)
        z2 = -beta_dry*x
        z[x<0] = z2[x<0]
        ifirst = np.nonzero(z>=zmax)[0][-1]
        ilast = np.nonzero(z<=zmin)[0][0]
        logger.info('ifirst= ', str(ifirst))
        logger.info('ilast= ', str(ilast))
        print('ifirst= ', str(ifirst))
        print('ilast= ', str(ilast))
        xt = x[ifirst:ilast]
        zt = z[ifirst:ilast]
        x = xt + abs(xt[0])         #added wrt matlab
        z = zt[::-1] + height               #added wrt matlab
#        logger.debug('z=', z)
#        logger.debug('x= ', x)
        return x, z

    def dean2(self):             #--> evt maken als in dean_beach_profile.m / dean1 en dean2 maken
        logger.debug('dean profile 2 is called for')    
        x = np.arange(-self.width, 0, self.dx)
        ws = ((self.s-1)*9.81*self.D50**2/(18*self.v))                          #eq 6.7 in coastal dynamics book  
        A = 0.5*ws**0.44        #0.51 in matlab                                                #eq 7.7 in coastal dynamics book  
        z = -abs(A*np.power(-1*x, self.m)) + self.height
        x += self.width   
        return x, z

    def hor(self):
        logger.debug('horizontal profile is called for')
        x = np.arange(0, self.width, self.dx)
        z = 0*x + self.height
        return x, z
    
    def sloping(self):   
        logger.debug('slope profile is called for')    
        x = np.arange(0, self.width, self.dx)                
        z = x * self.slope + self.height
        return x, z
    
    def yuniform(self, x, z):
        logger.debug('yuniform is called for')
        y = np.arange(0, self.length+self.dy, self.dy)
        X,Y = np.meshgrid(x, y)
        Z = np.tile(z, (len(y),1))              
        return X, Y, Z
    
###SPECIFIC BATHYMETRY PROFILES###
    def dune_1d(self, **kwargs):               
        logger.debug('dune_1d is called for')
        self.width = self.shorewidth
        xshore, zshore = self.dean2() 
        self.width = self.dunewidth + self.dx
        self.slope = self.duneslope
        xdune, zdune = self.sloping()   
        
        self.x = []     
        self.x.extend(xshore)
        self.x.extend(xdune + xshore[-1] + self.dx)
        
        self.z = []      
        self.z.extend(zshore)
        self.z.extend(zdune)
            
    def dune_2d(self, **kwargs):
        logger.debug('dune_2d is called for')
        self.dune_1d()
        self.x, self.y, self.z = self.yuniform(self.x, self.z)
          
    def flat_1d(self, **kwargs):
        logger.debug('flat_1d is called for')
        self.width = self.shorewidth + self.dunewidth + self.dx
        self.x, self.z = self.hor()
    
    def flat_2d(self, **kwargs):
        logger.debug('flat_2d is called for')
        self.flat_1d()
        self.x, self.y, self.z = self.yuniform(self.x, self.z)
        
    def dean1_2d(self, zmin, zmax, beta_dry, height, **kwargs):
        logger.debug('dean1_2d is called for')
#        self.width = self.shorewidth + self.dunewidth + self.dx   --> je geeft de width zelf al op
        self.x, self.z = self.dean1(zmin, zmax, beta_dry, height)
        self.x, self.y, self.z = self.yuniform(self.x, self.z)