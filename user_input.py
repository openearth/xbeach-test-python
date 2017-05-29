#'XBeach Diagnostic Test Model Generator'
#-User input specification-
#V0.0 Leijnse  29-05-17

import logging

logging.basicConfig(filename='logfile.log', format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s', level=logging.INFO)     #, filemode='w' WERKT NIET LEKKER
logger = logging.getLogger(__name__)
logger.info('user_input.py is called for') #logger.info


#%%GENERAL#####################################################################

diroutmain = "C:/Users/Leijnse/Desktop/XBeach_Diagnostic_Test_Model_Generator/" #including / at the end

#%%DIAGNOSTIC TEST SPECIFIC MODEL INPUT########################################


###DICTIONARY WITH PARAMETERS FOR XBEACH INPUT#################################
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
        mmpi = 1,   #Dit zijn de standaard waarden die later worden overschreven
        nmpi = 1,   #Dit zijn de standaard waarden die later worden overschreven
        mpiboundary = 'man',
        #boundaries
        front = 'wall',     
        back = 'wall',
        left = 'wall',
        right = 'wall',
        #other
        D50 = 200e-6,
        morstart = 0,        #???OF OP DE DEFAULT VAN 120s??? 
        morfac = 1,     #Dit zijn de standaard waarden die later worden overschreven
        dzmax = 1,      #Dit zijn de standaard waarden die later worden overschreven    #als default op 0.05 zetten?
        zs0 = 0,        #Dit zijn de standaard waarden die later worden overschreven
        wetslp = 0.3,                                                           #Critical under water avalanching slope, XBeach default = 0.3 (-)
        dryslp = 1.0,                                                           #Critical dry avalanching slope, XBeach default = 1.0 (-)        
        #output
        tintg = 100,  #NAAR DEZE WAARDE NOG EVEN KRITISCH KIJKEN
        tstop = 1800,    #Dit zijn de standaard waarden die later worden overschreven
        nglobalvar = ['zb','zs']) 



###CASES USER INPUT############################################################
   
#varied values other than specified in dictionary p
usermorfac = [10]                                                               #You can add another case by making this for instance [5,10]
userdzmax = [0.05]                                                              #When adding another varied parameters is required more actions are necessary, see end of script
userzs0 = [-1, 45]
#for dzmax<1 tstop should be larger (tstoplong):
tstoplong = 3600 #KAN NOG WEL AANGESCHERPT WORDEN 


#%%DICTIONARY FOR OTHER USER INPUT#############################################      -->OF hoeven deze waarden niet in een dictionary??? en
u = dict(diroutmain = diroutmain,           #!!!usercase/cases/morfaclist/dzmaxlist/zslist worden later hieraan toegevoegd
         module = 'Avalanching1_2',
         tests = ['pos_x','neg_x','pos_y','neg_y','hor'],                       #The different tests correspond to the direction of avalanching,for the horizontal case there should be no avalanching
         #specify runs per direction                                            #Specifies MPI-options per run. benchmark = 2D m1n1 (2D model with no MPI-boundaries). '2D m3n1' is a 2D model divided into 3 submodels in m-direction, and 1 on n-direction
         runs = ['benchmark','m1','m3','m3n1','m1n3','m3n3'],                   #Test'hor' is also treated as in x-direction, for pos_y and neg_y the runs 'm1' and 'm3' are not made.
         #waves
         waves = 'no',
         ow = [],                                                               #Wave parameters should be specified if waves = ['yes'], see xbeach.py for input description 
         #bathymetry
         shape = ['dune','dune','dune','dune','flat'],  #KAN WEG??              #Specify the bathymetry shape per test (in setup it distinguishes 1D/2D)    %TOCH?
         duneslope = 1.5,                                                           #Dune slope for the option 'dune'
         height = 0,                                                            #to heighten the profile
         length = 150,                                                          #length of the model in y-direction (longshore uniform)
         shorewidth = 60,                                                       #An indication of the model size (m) outside of the dune
         dunewidth = 30,                                                        #The width of the dune (m) if shape = 'dune'
         grex = 3,                                                               #Number of grid cells to extend the modeldomain at dune and offshore boundary
         grextype = 'both')                                                     #Option for extending the grid by a number of grid cells specified by 'grex'
                                                                                #'both boundaries' enables the addition of grex on both sides, 
                                                                                #'no boundaries' disables the addition of grex on both sides, 
                                                                                #'dune boundary' enables the addition of grex on the dune boundary side 
                                                                                #'offshore boundary' only at the offshore boundary side
         
                                                                                
#%%CHECKS######################################################################
###DICTIONARY FOR CHECKS###

wetslp = p['wetslp']
dryslp = p['dryslp']
c = dict(               #HIER IETS ZEGGEN OVER CHECKS DIE PERMANENT AAN STAAN??
        individualchecks=['Bed level change','Mass balance','Slope m-direction','Slope n-direction','MPI m-direction','MPI n-direction'], 
        #WIL JE DIT OOK NOG PER TEST AAN/UIT KUNNEN ZETTEN?
            #BIJ 'HORIZONTAL' WIL JE BIJV JUIST DAT ER GEEN BED LEVEL CHANGE IS, EN GEEN SLOPE ETC
            #MOET JE DAN KUNNEN INGEVEN WANNEER JE SUCCES HEBT??
            #OF JUIST DAN JE BIJ HORIZONTAL ALLEEN MASS BALANCE HEBT --> DAN ZOU JE DUS VAN 'INDIVIDUAL CHECKS' EEN MATRIX KUNNEN MAKEN MET HET AANTAL TESTS ALS RIJEN
        
        mpiconstraint = 0.1, #% dat het meer of minder mag zijn
        
        slopeconstraint = 0.1, #% dat het meer of minder mag zijn
        slopelocations = [2,12,30,44], #grid cell in the direction perpendicular to the dune
        slopetheoretical = [0,0.015,wetslp,dryslp],   #there should be as many values for 'slopetheoretical' as for 'slopelocations'
        
        massbalanceconstraint = 5, #m3     #???--> Wil je dit ingeven in m3/m of wil je een waarde voor een massbalancepercentage ingeven???
        
        comparisonchecks=['Benchmark','Runs']) #in de zin van 'benchmark'=vergelijk runs uitkomst met benchmark, 'runs'=vergelijk resultaat met run uit andere cases oid, 'cases', 'tests' etc
        



    
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


