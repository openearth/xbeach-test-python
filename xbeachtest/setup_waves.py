#'XBeach Diagnostic Test Model Generator'
# Creating the input files and folder structures

#%%GENERAL#####################################################################

import logging
import os 
import numpy as np
from bathy import Bathymetry
from user_input_waves import b, p, u, w
from xbeachtools import XBeachModel
from xbeachtools import XBeachBathymetry

logger = logging.getLogger(__name__)
logger.info('setup.py is called for')

#%%MAKING THE FOLDER STRUCTURE#################################################

###MODULES###
logger.info( u['module'])

###TESTS### 
for i in range(len(u['tests'])): 
    logger.info(u['tests'][i])
    
    p['cyclic'] = u['cyclic'][i]
    p['lateralwave'] = u['lateralwave'][i]
    
###CASES### 
    for j in range(len(u['cases'])):    
        logger.info(u['cases'][j])
        
        w['mainang'] = u['mainang'][j]
        
###SUBCASES###  
        for jj in range(len(u['subcases'])):    
            logger.info(u['subcases'][jj])
            
            w['s'] = u['s'][jj]
                    
###RUNS###               
            for k in range(len(u['runs'])):
                logger.debug(u['runs'][k])
                
                path = os.path.join(u['diroutmain'],
                                    u['module'],
                                    u['tests'][i],
                                    u['cases'][j],
                                    u['subcases'][jj],
                                    u['runs'][k])
    
                if not os.path.exists(path):
                    os.makedirs(path)     
                
                if u['runs'][k] in ['benchmark']:   
                    p['mmpi']  = 1
                    p['nmpi'] = 1
                    nprocesses = 1
                    
                elif u['runs'][k] in ['m3n1']:
                    p['mmpi']  = 3
                    p['nmpi'] = 1
                    nprocesses = 3
                    
                elif u['runs'][k] in ['m1n3']:
                    p['mmpi']  = 1
                    p['nmpi'] = 3
                    nprocesses = 3
                    
                elif u['runs'][k] in ['m3n3']:
                    p['mmpi']  = 3
                    p['nmpi'] = 3
                    nprocesses = 9
                            
    ###MAKING THE BATHYMETRIES AND CREATING THE XBEACH INPUT FILES###
                xb = XBeachModel(**p)
                bp = b.copy()
                bp.update(p)
                
                bathy = Bathymetry(**bp)                             
                bathy.dean1_2d(zmin = b['zmin'], zmax = b['zmax'], beta_dry = b['beta_dry'], height = b['height'])    
                
                XBbathy = XBeachBathymetry(bathy.x, bathy.y, bathy.z)                         
                XBbathy.gridextend(grextype= b['grextype'], grex= b['grex'], dx= p['dx'])
                                          
                xb['bathymetry'] = XBbathy                                          #bypassing xb.set_bathymetry                                   
                xb.write(path)   
                
                #making jonswap.txt:
                with open(os.path.join(path, 'jonswap.txt'), 'w') as fp:
                    fp.write('Hm0 = %0.6f\n' % w['Hm0'])
                    fp.write('Tp = %0.6f\n' % w['Tp'])
                    fp.write('mainang = %0.6f\n' % w['mainang'])   
                    fp.write('s = %0.6f\n' % w['s'])
                    fp.write('gammajsp = 3.3\n')    
                    fp.write('fnyq = 0.3\n')
                    fp.close()    
                    
                #making shell executable:            
                nodes = np.ceil(nprocesses/4.)
                fname = 'diag'
                with open(os.path.join(path, 'run.sh'), 'w') as fp  :
                    fp.write('#!/bin/sh\n')
                    fp.write('#$ -cwd\n')
                    fp.write('#$ -j yes\n')
                    fp.write('#$ -V\n')
                    fp.write('#$ -N %s\n' % fname)
                    fp.write('#$ -q normal-e3\n')
                    fp.write('#$ -pe distrib %d\n\n' % nodes)
                    
                    fp.write('module purge\n')
                    fp.write('module load gcc/4.9.2\n')
                    fp.write('module load hdf5/1.8.14_gcc_4.9.2\n')
                    fp.write('module load netcdf/v4.3.2_v4.4.0_gcc_4.9.2\n')
                    fp.write('module load openmpi/1.8.3_gcc_4.9.2\n')
                    fp.write('module load /opt/xbeach/modules/xbeach-%s_gcc_4.9.2_1.8.3_HEAD\n\n' % (os.getenv('XBEACH_PROJECT_ID')))
                    fp.write('module list\n\n')
                                    
                    fp.write('mpirun -report-bindings -np %d -map-by core xbeach\n\n' % (nprocesses+1))
