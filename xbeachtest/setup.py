#'XBeach Diagnostic Test Model Generator'
# Creating the input files and folder structures

#%%GENERAL#####################################################################

import logging
import os 
import posixpath
import numpy as np
from bathy import Bathymetry
from user_input import b, p, u
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
    
###CASES### 
    for j in range(len(u['cases'])):    
        logger.info(u['cases'][j])
        
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
            
            path = os.path.join(u['diroutmain'],
                                u['module'],
                                u['tests'][i],
                                u['cases'][j],
                                runs[k])
            # Also create a unix compatible path to use in .sh script
            unixpath = posixpath.join(os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION_UNIX'),
                                u['module'],
                                u['tests'][i],
                                u['cases'][j],
                                runs[k])
            if not os.path.exists(path):
                os.makedirs(path)     
            
            if runs[k] in ['m1','benchmark']:   
                p['mmpi']  = 1
                p['nmpi'] = 1
                nprocesses = 1
                
            elif runs[k] in ['m3', 'm3n1']:
                p['mmpi']  = 3
                p['nmpi'] = 1
                nprocesses = 3
                
            elif runs[k] in ['m1n3']:
                p['mmpi']  = 1
                p['nmpi'] = 3
                nprocesses = 3
                
            elif runs[k] in ['m3n3']:
                p['mmpi']  = 3
                p['nmpi'] = 3
                nprocesses = 9
                        
###MAKING THE BATHYMETRIES AND CREATING THE XBEACH INPUT FILES###
            xb = XBeachModel(**p)
            bp = b.copy()
            bp.update(p)
            bathy = Bathymetry(**bp)
                         
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
                                
                fp.write('mpirun -report-bindings -np %d -map-by core -wdir %s xbeach\n\n' % (nprocesses+1, unixpath))
