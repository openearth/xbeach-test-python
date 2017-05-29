# 'XBeach Diagnostic Test Model Generator'
# Setup of model
# V0.8 Leijnse -- 29-05-17
   
#%%GENERAL#####################################################################
from xbeachtools import XBeachModel
import os 
import logging
import json
from bathy import Bathymetry
from user_input import p,u

logger = logging.getLogger(__name__)
logging.info('setup.py is called for')

#%%MAKING THE FOLDER STRUCTURE#################################################
###MODULES###
logger.info( u['module'])

###TESTS### 
for i in range(len(u['tests'])): 
    logger.info( u['tests'][i])
    
###CASES### 
    for j in range(len(u['cases'])):    
        logger.info( u['cases'][j])
        
        p['morfac'] = u['morfaclist'][j]
        p['zs0']    = u['zs0list'][j]
        p['dzmax']  = u['dzmaxlist'][j]
        p['tstop']  = u['tstoplist'][j]
        
        if u['tests'][i] in ['pos_y','neg_y']:   
            runs = ['benchmark','m3n1','m1n3','m3n3']
        else:
            runs = u['runs']
                    
###RUNS###               
        for k in range(len(runs)):
            logger.debug(runs[k])
            
            mpiboundary = 'man'            
            if runs[k] in ['m1','benchmark']:   
                mmpi = 1
                nmpi = 1
            elif runs[k] in ['m3', 'm3n1']:
                mmpi = 3
                nmpi = 1
            elif runs[k] in ['m1n3']:
                mmpi = 1
                nmpi = 3
            elif runs[k] in ['m3n3']:
                mmpi = 3
                nmpi = 3
            
            p['mmpi'] = mmpi    #OVerschrijven van de standaard waarde die nu in de p-dictionary staat
            p['nmpi'] = nmpi
            
            #%%MAKING THE PARAMS.TXT FILES###            
            path = (u['diroutmain']   + u['module'] + '/' + u['tests'][i] + '/' + u['cases'][j] + '/' + runs[k] + '/')
            os.makedirs(path, exist_ok=False)    
            
            xb = XBeachModel(**p)  
                             
            bathy = Bathymetry(u['dunewidth'], u['shorewidth'], p['dx'], p['dy'])
            
            if u['shape'][i] in ['flat']:      
                if runs[k] in ['m1','m3']:
                    x,z = bathy.flat_1d(**p, **u)                            
                else:
                    x,y,z = bathy.flat_2d(**p, **u)         
                     
            if u['shape'][i] in ['dune']:
                if runs[k] in ['m1','m3']:
                    x,z = bathy.dune_1d( **p, **u)                          
                else:
                    x,y,z = bathy.dune_2d(**p, **u) 
                      
            if runs[k] in ['m1','m3']:  #1D runs
                if u['tests'][i] in ['neg_x']:
                    xb.set_bathymetry(x, z, dx= p['dx'], mirror= False, turn= False, grex= u['grex'], grextype= u['grextype'])
                elif u['tests'][i] in ['pos_x']:
                    xb.set_bathymetry(x, z, dx= p['dx'], mirror= True, turn= False, grex= u['grex'], grextype= u['grextype'])
                elif u['tests'][i] in ['neg_y']:
                    xb.set_bathymetry(x, z, dx= p['dx'], mirror= False, turn= True, grex= u['grex'], grextype= u['grextype'])
                elif u['tests'][i] in ['pos_y']:
                    xb.set_bathymetry(x, z, dx= p['dx'], mirror= True, turn= True, grex= u['grex'], grextype= u['grextype'])    #Kan dit nog compacter? --> JA hier vraag je dan allen .mirror   xb.set_bathymetry moet al hiervoor gezet worden
                else:                                                           #is meant for 'hor', treated as neg_x
                    xb.set_bathymetry(x, z, dx= p['dx'], mirror= False, turn= False, grex= u['grex'], grextype= u['grextype'])
                    
            else:   #2D runs
                if u['tests'][i] in ['neg_x']:
                    xb.set_bathymetry(x, y, z, dx= p['dx'], mirror= False, turn= False, grex= u['grex'], grextype= u['grextype'])
                elif u['tests'][i] in ['pos_x']:
                    xb.set_bathymetry(x, y, z, dx= p['dx'], mirror= True, turn= False, grex= u['grex'], grextype= u['grextype'])
                elif u['tests'][i] in ['neg_y']:
                    xb.set_bathymetry(x, y, z, dx= p['dx'], mirror= False, turn= True, grex= u['grex'], grextype= u['grextype'])
                elif u['tests'][i] in ['pos_y']:
                    xb.set_bathymetry(x, y, z, dx= p['dx'], mirror= True, turn= True, grex= u['grex'], grextype= u['grextype'])
                else:                                                           #is meant for 'hor', treated as neg_x
                    xb.set_bathymetry(x, y, z, dx= p['dx'], mirror= False, turn= False, grex= u['grex'], grextype= u['grextype'])

            if u['waves'] in ['yes']:
                xb.set_waves(u['ow']) 
            
            xb.write(path)   
                      
#%%MAKING THE OTHERUSERINPUT.TXT FILE##############################   
os.chdir(u['diroutmain']  + '/' ) #+ u['module']) 
with open('Udictionary.txt', 'w') as f:
    json.dump(u,f, indent=4)

