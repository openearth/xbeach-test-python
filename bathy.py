#'XBeach Diagnostic Test Model Generator'
# Creating different profile shapes
# V0.0 Leijnse -- 15-05-17

import numpy as np
from xbeachtools import XBeachBathymetry
import logging

logger = logging.getLogger(__name__)
logging.info('bathy.py is called for')

#==============================================================================
# # return XBeachBathymetry(x, z)  --> hoe zou dat werken??  
#==============================================================================

class Bathymetry:  #(XBeachBathymetry)     #(XBeachParams) ??
    def __init__(self, dunewidth, shorewidth, dx, dy, *args):  #OF HIER MEER OF MINDER BIJ???
        self.dunewidth = dunewidth
        self.shorewidth = shorewidth
        self.dx = dx
        self.dy = dy

    ### GENERAL BUILDING BLOCKS###
    def dean(self, width, D50, height= 0, m= 0.67, s= 1.6, v= 1e-6):     #Mocht je ook dean boven water willen moet dat apart even bekeken worden of dit goed gaat. --> height optie is hiervoor bedoeld
        logger.debug('dean profile is called for')    
        x = np.arange(-width, 0, self.dx)
        A = 0.5*((s-1)*9.81*D50**2/(18*v))**0.44     #Nog een keer opzoeken of overige waarden als 18, 0.44 ook variabelen moeten worden
        z = -abs(A*np.power(-1*x, m)) + height
        x += width   
        return x, z

    def hor(self, width, height= 0):
        logger.debug('horizontal profile is called for')
        x = np.arange(0, width, self.dx)
        z = 0*x + height
        return x, z
    
    def slope(self, width, slope, height= 0):   
        logger.debug('slope profile is called for')    
        x = np.arange(0, width, self.dx)                
        z = x * slope + height
        return x, z
    
    def yuniform(self, x, z, length):
        logger.debug('yuniform is called for')
        y = np.arange(0, length+self.dy, self.dy)
        X,Y = np.meshgrid(x, y)
        Z = np.tile(z, (len(y),1))              
        return X,Y,Z
    
    ###SPECIFIC BATHYMETRY PROFILES###
    def dune_1d(self, D50, duneslope, *args, height=0, **kwargs):               #Profile consists of a Dean profile for the shore and a linear slope for the dune
        logger.debug('dune_1d is called for')       #
        xshore, zshore = self.dean(self.shorewidth, D50, height) #self.shorewidth kan weg
        xdune, zdune = self.slope(self.dunewidth+self.dx, duneslope, height)    #kijken of hier self. weg kan
        x = []     
        x.extend(xshore)
        x.extend(xdune+ xshore[-1]+ self.dx)
        z = []      #ipv return wordt dit self.z
        z.extend(zshore)
        z.extend(zdune)
        return x,z
    
    def dune_2d(self, D50, duneslope, length, *args, height= 0, **kwargs):
        logger.debug('dune_2d is called for')
        x,z = self.dune_1d(D50, duneslope, height)
        X,Y,Z = self.yuniform(x, z, length)
        return X,Y,Z
    
    def flat_1d(self, height, *args, **kwargs):
        logger.debug('flat_1d is called for')
        x,z = self.hor(self.shorewidth + self.dunewidth+self.dx, height)
        return x,z
    
    def flat_2d(self, length, height, *args, **kwargs):
        logger.debug('flat_2d is called for')
        x,z = self.flat_1d(height)
        X,Y,Z = self.yuniform(x, z, length)
        return X,Y,Z
    
