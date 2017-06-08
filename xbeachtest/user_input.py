#'XBeach Diagnostic Test Model Generator'
# Specification of the desired parameters and options by the user

#%%GENERAL#####################################################################

import json
import logging

logging.basicConfig(filename='xbeachtest-logfile.log', format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s', level=logging.INFO) #.DEBUG)    
logger = logging.getLogger(__name__)
logger.info('user_input.py is called for') 

diroutmain = "C:/Users/Leijnse/Desktop/Checkouts/openearth/xbeach-test-python/xbeachtest/" #including / at the end

#%%INPUT FOR SETUP OF MODELS###################################################

###DICTIONARY WITH PARAMETERS FOR XBEACH params.txt###
p = dict(
        #processes
        swave=0,
        lwave=0,
        flow=0,
        sedtrans = 1,
        morphology = 1,
        avalanching = 1,
        nonh = 0,
        #grid
        dx = 2,  
        dy = 2,
        vardx = 1,
        posdwn = -1,        
        mmpi = 1,   
        nmpi = 1,   
        mpiboundary = 'man',
        #boundaries
        front = 'wall',     
        back = 'wall',
        left = 'wall',
        right = 'wall',
        #other
        D50 = 200e-6,
        morstart = 0,       
        morfac = 1,     
        dzmax = 1,      
        zs0 = 0,        
        wetslp = 0.3,                                                          
        dryslp = 1.0,                                                                  
        #output
        tintg = 100,  
        tstop = 600,    
        nglobalvar = ['zb','zs']) 


###CASES USER INPUT###   
#Varied values other than specified in dictionary p                             (in setup file the values of p-dictionary are over-written)
usermorfac = [10]                                                              
userdzmax = [0.05]                                                              
userzs0 = [-1, 45]
tstoplong = 3000 


###DICTIONARY FOR BATHYMETRY INPUT###   
b = dict(shape = ['dune','dune','dune','dune','flat'], 
         duneslope = 1.5,                                                          
         height = 0,                                                            
         length = 150,                                                          
         shorewidth = 60,                                                       
         dunewidth = 30,                                                        
         grex = 3,                                                               
         grextype = 'both')  

    
###DICTIONARY FOR OTHER USER INPUT###    
u = dict(diroutmain = diroutmain,                                               #cases/morfaclist/dzmaxlist/zslist/tstoplist are added to this library in the section below
         module = 'Avalanching',
         tests = ['pos_x','neg_x','pos_y','neg_y','hor'],                                                                  
         runs = ['benchmark','m1','m3','m3n1','m1n3','m3n3'],                   #benchmark = m1n1               
         waves = 'no',
         ow = [])            
                                                   
    
#%%VARYING PARAMETERS IN CASES#################################################     

usercase = len(usermorfac)+len(userdzmax)+len(userzs0)+1                        #+1 for the standard case
cases = [0]*usercase
cases[-1]=("standard")
morfaclist = [p['morfac']]*usercase
dzmaxlist = [p['dzmax']]*usercase
zs0list = [p['zs0']]*usercase
tstoplist = [p['tstop']]*usercase
    
for j in range(len(usermorfac)):
    tempmorfac = str(usermorfac[j])
    cases[j] = ("morfac_" + tempmorfac)
    morfaclist[j] = float(tempmorfac)   
    
for j in range(len(userdzmax)):
    tempdzmax = str(userdzmax[j])
    cases[len(usermorfac)+j] = ("dzmax_" + tempdzmax)
    dzmaxlist[len(usermorfac)+j] = float(tempdzmax)    
    
for j in range(len(userzs0)):
    tempzs0 = str(userzs0[j])
    cases[len(usermorfac)+len(userdzmax)+j] = ("zs0_" + tempzs0)
    zs0list[len(usermorfac)+len(userdzmax)+j] = float(tempzs0)  

for j in range(usercase):
    if dzmaxlist[j]< p['dzmax']:
        tstoplist[j] = tstoplong

u['cases'] = cases
u['morfaclist'] = morfaclist
u['dzmaxlist'] = dzmaxlist
u['zs0list'] = zs0list
u['tstoplist'] = tstoplist


#%%INPUT FOR ANALYSIS OF RESULTS###############################################

###DICTIONARY FOR CHECKS###

wetslp = p['wetslp']
dryslp = p['dryslp']

c = dict(               
        checks_ind=['bedlevelchange','massbalance','m_slope','n_slope','m_mpi','n_mpi'], 
        checks_comp=['benchmarkcomp_m', 'benchmarkcomp_n'], 
               
        mpicon = 0.1, 
        mpinr = -1,
        slpcon = 0.1, 
        slploc = [2,12,30,44], 
        slptheo_cross = [0,0.015,wetslp,dryslp],   
        slptheo_long = [0,0,0,0],        
        rmsecon = 0.2,
        massbalancecon = 5) 
        

#%%MAKING THE DICTIONARY TEXT FILES############################################ 

with open('Bdictionary.txt', 'w') as f:
    json.dump(b, f, indent=4)

with open('Cdictionary.txt', 'w') as f:
    json.dump(c, f, indent=4)

with open('Pdictionary.txt', 'w') as f:
    json.dump(p, f, indent=4)
    
with open('Udictionary.txt', 'w') as f:
    json.dump(u, f, indent=4)  