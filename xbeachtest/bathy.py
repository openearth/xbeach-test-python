#'XBeach Diagnostic Test Model Generator'
# Making bathymetry profiles

import numpy as np
from xbeachtools import XBeachBathymetry
import logging

logger = logging.getLogger(__name__)
logger.info('bathy.py is called for')

class Bathymetry(XBeachBathymetry):  
    def __init__(self, dx= 1, dy= 1, width= 100, dunewidth=25, shorewidth= 75, length= 0, height= 0, slope = 1, duneslope= 1, D50= 200e-6, m= 0.67, s= 1.6, v= 1e-6, **kwargs):  
    
        self.x = None #x = None
        self.y = None #y = None
        self.z = None #z = None
        
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
    def dean(self):     
        logger.debug('dean profile is called for')    
        x = np.arange(-self.width, 0, self.dx)
        ws = ((self.s-1)*9.81*self.D50**2/(18*self.v))                          #eq 6.7 in coastal dynamics book  
        A = 0.5*ws**0.44                                                        #eq 7.7 in coastal dynamics book  
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
        xshore, zshore = self.dean() 
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

#TO DO:    

#moeten hier dan nog dingen als asarray en reshape gebeuren als in xbeach.py??? --> omdat je het nu als XBeachBathymetry object uitgeeft
    #dit lijkt nog niet goed te gaan
#        super(Bathymetry, self).__init__()  nodig?