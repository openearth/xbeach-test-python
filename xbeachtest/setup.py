#'XBeach Diagnostic Test Model Generator'
# Creating the input files and folder structures

#%%GENERAL#####################################################################

import json
import logging
import os 
from bathy import Bathymetry
from user_input import b,p,u
from xbeachtools import XBeachModel
from xbeachtools import XBeachBathymetry

logger = logging.getLogger(__name__)
logger.info('setup.py is called for')

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
            
            path = (u['diroutmain']   + u['module'] + '/' + u['tests'][i] + '/' + u['cases'][j] + '/' + runs[k] + '/')
            os.makedirs(path, exist_ok=False)     
            
            if runs[k] in ['m1','benchmark']:   
                p['mmpi']  = 1
                p['nmpi'] = 1
                shell = 'xbeach'
                
            elif runs[k] in ['m3', 'm3n1']:
                p['mmpi']  = 3
                p['nmpi'] = 1
                shell = 'mpirun -n 4 xbeach'
                
            elif runs[k] in ['m1n3']:
                p['mmpi']  = 1
                p['nmpi'] = 3
                shell = 'mpirun -n 4 xbeach'
                
            elif runs[k] in ['m3n3']:
                p['mmpi']  = 3
                p['nmpi'] = 3
                shell = 'mpirun -n 10 xbeach'
                        
###MAKING THE BATHYMETRIES AND CREATING THE XBEACH INPUT FILES###
            xb = XBeachModel(**p)  
            bathy = Bathymetry(**b, **p)
                         
            if runs[k] in ['m1','m3']:
                if b['shape'][i] in ['flat']: 
                    bathy.flat_1d()
                elif b['shape'][i] in ['dune']:    
                    bathy.dune_1d() 
                XBbathy = XBeachBathymetry(bathy.x, bathy.z)                   
                        
            else:
                if b['shape'][i] in ['flat']:
                    bathy.flat_2d()
                elif b['shape'][i] in ['dune']:
                    bathy.dune_2d()
                XBbathy = XBeachBathymetry(bathy.x, bathy.y, bathy.z)
                     
            XBbathy.gridextend(grextype= b['grextype'], grex= b['grex'], dx= p['dx'])
                       
            if runs[k] in ['m1','m3']:  
                if u['tests'][i] in ['pos_x']:
                    XBbathy.mirror()

            else:  
                if u['tests'][i] in ['pos_x']:
                    XBbathy.mirror()
                elif u['tests'][i] in ['neg_y']:
                    XBbathy.turn()                
                elif u['tests'][i] in ['pos_y']:
                    XBbathy.mirror()
                    XBbathy.turn()
            
            xb['bathymetry'] = XBbathy                                          #bypassing xb.set_bathymetry

            if u['waves'] in ['yes']:
                xb.set_waves(u['ow']) 
            
            xb.write(path)   
            
            #making shell executable:            
            os.chdir(path)            
            with open('run.sh', 'w') as f:  
                json.dump(shell, f, indent=4)