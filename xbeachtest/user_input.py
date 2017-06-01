import logging
import json

logging.basicConfig(filename='logfile.log', format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s', level=logging.DEBUG) #INFO)    
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
        posdwn = 0,
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
        dzmax = 1,      #als default op 0.05 zetten?
        zs0 = 0,        
        wetslp = 0.3,                                                          
        dryslp = 1.0,                                                                  
        #output
        tintg = 100,  #NAAR DEZE WAARDE NOG EVEN KRITISCH KIJKEN
        tstop = 1800,    #Dit zijn de standaard waarden die later worden overschreven
        nglobalvar = ['zb','zs']) 



###CASES USER INPUT###
   
#Varied values other than specified in dictionary p     (in setup file the values of p-dictionary are over-written)
usermorfac = [10]                                                              
userdzmax = [0.05]                                                              
userzs0 = [-1, 45]
tstoplong = 3600 #KAN NOG WEL AANGESCHERPT WORDEN , dit wordt later getest en toegevoegd aan dictionary u

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
u = dict(diroutmain = diroutmain,           #!!!usercase/cases/morfaclist/dzmaxlist/zslist worden later hieraan toegevoegd
         module = 'Avalanching',
         tests = ['pos_x','neg_x','pos_y','neg_y','hor'],                                                                  
         runs = ['benchmark','m1','m3','m3n1','m1n3','m3n3'],                   
         waves = 'no',
         ow = [])            
                                                   
    
#%%ADAPT WHEN ADDING MORE TYPE OF PARAMETERS TO CASES##########################     --> !!!KIJKEN OF DIT NOG ANDERS MOET/Variable matrix!!! OF EVT IN SETUP.py
usercase = len(usermorfac)+len(userdzmax)+len(userzs0)+1                         #+1 for the standard case
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

#u['usercase'] = usercase
u['cases'] = cases
u['morfaclist'] = morfaclist
u['dzmaxlist'] = dzmaxlist
u['zs0list'] = zs0list
u['tstoplist'] = tstoplist

#--> Go to setup.py
#Within the case-for-loop the following should be extended:
#       morfac = morfaclist[j]
#       dzmax = dzmaxlist[j]
#       zs = zslist[j]    
#    
#Also look at tstop = standardtstop OR customtstop  


#%%INPUT FOR ANALYSIS OF RESULTS###############################################


###DICTIONARY FOR CHECKS###

wetslp = p['wetslp']
dryslp = p['dryslp']

c = dict(               #HIER IETS ZEGGEN OVER CHECKS DIE PERMANENT AAN STAAN??
        individualchecks=['bedlevelchange','massbalance','m_slope','n_slope','m_mpi','n_mpi'], 
        comparisonchecks=['Benchmark','Runs'], #in de zin van 'benchmark'=vergelijk runs uitkomst met benchmark, 'runs'=vergelijk resultaat met run uit andere cases oid, 'cases', 'tests' etc
               
        mpiconstraint = 0.1, #% dat het meer of minder mag zijn (0.1 BETEKEND 1+0.1=1.1 --> IS 10% MEER OF 1-0.1=0.9 IS 10 %MINDER)
        
        slpcon = 0.1, #% dat het meer of minder mag zijn
        slploc = [2,12,30,44], #+grex nog?, #grid cell in the direction perpendicular to the dune (LET OP OP GRIDEXTEND!)
        slptheo_cross = [0,0.015,wetslp,dryslp],   #there should be as many values for 'slopetheoretical' as for 'slopelocations'
        slptheo_long = [0,0,0,0],
        
        massbalanceconstraint = 5) #m3     #???--> Wil je dit ingeven in m3/m of wil je een waarde voor een massbalancepercentage ingeven???
        

#%%MAKING THE DICTIONARY TEXT FILES############################################ 
with open('Bdictionary.txt', 'w') as f:
    json.dump(b, f, indent=4)

with open('Cdictionary.txt', 'w') as f:
    json.dump(c, f, indent=4)

with open('Pdictionary.txt', 'w') as f:
    json.dump(p, f, indent=4)
    
with open('Udictionary.txt', 'w') as f:
    json.dump(u, f, indent=4)  