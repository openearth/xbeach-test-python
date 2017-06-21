#'XBeach Diagnostic Test Model Generator'
# Specification of the desired parameters and options by the user

#%%GENERAL#####################################################################

import json
import logging
import os

diroutmain = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION')
#diroutmain = "P:/xbeach/skillbed/diagnostic/lastrun/"
#diroutmain = 'C:/Users/leijnse/Desktop/Checkouts/openearth/xbeach-test-python/xbeachtest/'

path = os.path.join(diroutmain, 'xbeachtest-waves-setup.log')

logging.basicConfig(filename= path, format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s', level=logging.DEBUG) #.DEBUG)    
logger = logging.getLogger(__name__)
logger.info('user_input.py is called for') 


#%%INPUT FOR SETUP OF MODELS###################################################

###DICTIONARY WITH PARAMETERS FOR XBEACH params.txt###
p = dict(
        #processes
        swave=1,
        lwave=1,
        flow=1, 
        sedtrans = 0,
        morphology = 0,
        avalanching = 0,
        cyclic = 0,
        nonh = 0,       
        #grid
        dx = 10,     
        dy = 20,
        vardx = 1,
        posdwn = -1,
        mmpi = 1,   
        nmpi = 1,   
        mpiboundary = 'man',
        #boundaries
        front = 'abs_2d',     
        back = 'wall',
        left = 'neumann',           #is also the default setting for XBeach
        right = 'neumann',          #is also the default setting for XBeach
        lateralwave = 'neumann',    #is varied between the tests
        #waves
        thetanaut = 1,
        thetamax   = 360, 
        thetamin   = 180, 
        dtheta     = 10 , 
        instat     = 'jons',
        bcfile     = 'jonswap.txt',
        #other
        D50 = 200e-6,
        zs0 = 0,                                                                        
        #output
        tintg = 10,  
        tstop = 600,    
        nglobalvar = ['zb','zs','H','ue','ve','ui','vi']) 


###DICTIONARY FOR WAVE INPUT###
w = dict(Hm0 = 3,
        Tp = 8,
        s = 10, 
        mainang = 270) 


###DICTIONARY FOR BATHYMETRY INPUT###   
b = dict(height = 2,  
         zmin = -17, 
         zmax = 3, 
         beta_dry = 0.1,                                                          
         length = 2000,                                                                                                                
         grex = 3,                                                               
         grextype = 'both')  

    
###DICTIONARY FOR OTHER USER INPUT###    
u = dict(diroutmain = diroutmain,           
         module = 'waves',
         
         tests = ['neumann', 'cyclic', 'wavecrest'], 
         cyclic = [0,1,0],
         lateralwave = ['neumann', 'cyclic', 'wavecrest'],
         
         cases = ['mainang_240', 'mainang_270', 'mainang_300'],
         mainang = [240, 270, 300], 
         
         subcases = ['s_10', 's_100000'],        #DIT TOEVOEGEN AAN SETUP EN ANALYZE_THIS!!!
         s = [10, 100000],
         
         runs = ['benchmark','m3n1','m1n3','m3n3'])            
                                                  

#%%INPUT FOR ANALYSIS OF RESULTS###############################################

###DICTIONARY FOR CHECKS###
c = dict(checks_ind= ['bedlevelchange_zb','bedlevelchange_zs','massbalance_zb','massbalance_zs','massbalance_intime','wave_generation_offshore','wave_generation_coast','n_Hrms'], 
        checks_comp= [],#'benchmarkcomp_m', 'benchmarkcomp_n'], 
        xloc1= 0,
        xloc2= 201,
        tstart= 5*60/p['tintg'],
        Hrmsconstraint= 0.10,
        massbalancecon_intime= 250000, #m3  
        massbalancecon_zs= 250000, #m3  
        massbalancecon_zb=1) #m3     
        

#%%MAKING THE DICTIONARY TEXT FILES############################################ 
with open(os.path.join(diroutmain, 'dictB_waves.txt'), 'w') as f:
    json.dump(b, f, indent=4)

with open(os.path.join(diroutmain, 'dictC_waves.txt'), 'w') as f:
    json.dump(c, f, indent=4)

with open(os.path.join(diroutmain, 'dictP_waves.txt'), 'w') as f:
    json.dump(p, f, indent=4)
    
with open(os.path.join(diroutmain, 'dictU_waves.txt'), 'w') as f:
    json.dump(u, f, indent=4)  
    
with open(os.path.join(diroutmain, 'dictW_waves.txt'), 'w') as f:
    json.dump(w, f, indent=4)