#'XBeach Diagnostic Test Model Generator'
# Analysis of model
#V0.0 Leijnse -- 15-05-17

#NU TOCH WEER HET UITLEZEN EN CHECKEN VAN DATA BIJ ELKAAR DOEN?? DAN KAN JE HET ALS LOSSESTUKJE CODE MODULES BESCHOUWEN (die je evt apart kan aanroepen)
#Maak onderscheid tussen insintrieke checks en checks tusssen runs/cases/tests
#De gekozen opties voor module/tests/cases/runs kunnen in een algemene test file worden geprint in de setupfile en dan uitgelezen  in de analyse file zodat je weet wat voor cases er zijn
    #Het doel is dan om te zorgen dat er in de analyze file niks meer veranderd hoeft te worden
    #Moeten ook nog de soorten checks die gedaan worden aangestuurd worden vanuit de setup file?
#%%GENERAL#####################################################################

#Info die in deze file moet belanden:
import numpy as np
#from oceanwaves import OceanWaves  
import os 
import netCDF4
import logging
import json
from user_input import c
logger = logging.getLogger(__name__)
logging.info('analyze_this.py is called for')

#heb je ook weer mpidims = xb_read_mpi_dims(dirin) (van Matlab) nodig?

with open('Udictionary.txt', 'r') as f:
    u = json.load(f)
    
if u == None:
    logger.info('dictionary u is not succesfully read from text file')
else:
    logger.info('dictionary u is read from text file')
#==============================================================================
# if tests[i] in ['positive y','negative y']:
#     runs = runsy
# else:
#     runs = runsx
#==============================================================================
#%%LOOPS
diroutmodules = (u['diroutmain'] + u['module'] + "/")
os.chdir(diroutmodules)     

for i in range(len(u['tests'])):
    dirouttests = (diroutmodules + u['tests'][i] + "/")
    os.chdir(dirouttests)
    
    for j in range(len(u['cases'])):    
        diroutcases = (dirouttests + u['cases'][j] + "/")        
        os.chdir(diroutcases)
        
        if u['tests'][i] in ['pos_y','neg_y']:   
            runs = ['benchmark','m3n1','m1n3','m3n3']
        else:
            runs = u['runs']
            
        for k in range(len(runs)):
            diroutruns = (diroutcases + runs[k] + "/")
            os.chdir(diroutruns)
      
            #%%READ XBEACH OUTPUT FILES########################################     #MOET DIT OOK IN EEN DICIONARY KOMEN OF HEEFT DAT WEINIG VOORDEEL?
            fname = diroutruns + "xboutput.nc" 

            with netCDF4.Dataset(fname, 'r') as xb:
                
                parameter = xb.variables['parameter']
                
                n = dict(
                    # read initial and final topography
                    zb0 = xb.variables['zb'][0,:,:],     
                    zbEnd = xb.variables['zb'][-1,:,:],
                    
                    # read initial and final water level
#                    zs0 = xb.variables['zs'][0,:,:],    
                    zsEnd = xb.variables['zs'][-1,:,:], #NIET MEER NODIG??? want geen plots meer...
                    
                    # read other parameters                   
                    dx = parameter.getncattr('dx'),
                    dy = parameter.getncattr('dy'),
                    nx = parameter.getncattr('nx'),
                    ny = parameter.getncattr('ny'),
                    mpi = parameter.getncattr('mpiboundary_str'),    #NOG NODIG???
                    mmpi = parameter.getncattr('mmpi'), 
                    nmpi = parameter.getncattr('nmpi')) 
            #==================================================================
            #     JE WILT EIGENLIJK NOG IETS DAT WERKT ALS xb_read_mpi_dims.m
            #       dit kan dan binnen de code of als extra .py bij GitHub
            #==================================================================
#                wetslp = parameter.getncattr('wetslp')
#                dryslp = parameter.getncattr('dryslp')
    
            #%%GENERAL PROCESSING##############################################
    
    
            #%%INDIVIDUAL CHECKS############################################### gehaald uit 'testcheck3.py'
            #            Allemaal met if individualchecks in ['bed level change'] ETC, je wilt dat alle opgegeven checks gedaan worden, dus niet if elif elif maar if if if!!!
            for l in range(len(c['individualchecks'])):
                
            #%%CHECKS OVER WHOLE GRID##########################################
                ###CHECK1: Bed level change#################################### #Look over whole grid if avalanching happens at all
                if c['individualchecks'][l] in ['Bed level change']:
                    print('Bed level check') #TEMP
                    #processing
                    zbDelta=np.mean(abs(n['zbEnd'] - n['zb0']))
                    #checking
                    if zbDelta>0:
                        check = 1                                                           #Succes
                        print('Check1: ', check) #TEMP
                    else:
                        check =0.5                                                          #Failure
                        print('Check1:',check,'--> mean of delta zb = 0') #TEMP
                    
                ###CHECK2: Mass balance########################################
                if c['individualchecks'][l] in ['Mass balance']:
                    print('Mass balance') #TEMP
                    #processing
                    mass0 = n['zb0'].sum() * n['dx'] * n['dy']
                    massEnd = n['zbEnd'].sum() * n['dx'] * n['dy']
            #        massDisplaced --> WIL JE DIE NOG BEREKENEN???
                    massbalance = massEnd - mass0   # WIL JE DIT NOG IN m3/m LATEN ZIEN OF IS DIT NIET RELEVANT MEER?
            #        massbalancepercentage --> WIL JE DIE NOG BEREKENEN???
            #        if ny==0:  --> DIE IS MISSCHIEN NIET NODIG DOORDAT NP.SUM OVER JE HELE MATRIX KAN!!! ITT MATLAB
                        
                    #checking
                    if massbalance > c['massbalanceconstraint']:
                        check = 0.5
                        print('Check2:',check,'--> too much mass entering the model')   #TEMP           
                    elif massbalance < -c['massbalanceconstraint']:
                        check = 0.5
                        print('Check2:',check,'--> too much mass leaving the model')  #TEMP           
                    else:
                        check = 1
                        print('Check2: ', check) #TEMP
                        
                        
            #%%CHECKS OVER MIDDLE TRANSECT#####################################  
                ###Making transects###
            #   Hier in beide richtingen een transect in het midden
            #   Nadenken over omgaan met 1D en gedraaid! --> even kijken wat er gebeurd als je een transect maakt van een 1D case
                
                if n['ny']==0:                                                                   #For 1D cases you do not have to take a transect, also no transect in n-direction
                    zb0transectm = n['zb0']
                    zbEndtransectm = n['zbEnd']
                else:                                                                       #2D cases
                    transectm = round(np.shape(n['zbEnd'])[0]/2)                                 #n-location of central transect in m direction
                    transectn = round(np.shape(n['zbEnd'])[1]/2)                                 #m-location of central transect in n direction  
                    zb0transectm = n['zb0'][transectm, :]    #NODIG? /ER MAAR IN LATEN??
                    zb0transectn = n['zb0'][:,transectn]
                    zbEndtransectm = n['zbEnd'][transectm, :]   #ITT MATLAB FILE HET DRAAIEN VAN DE TRANSECT PAS DOEN BIJ DE DAADWERKELIJKE CHECK?
                    zbEndtransectn = n['zbEnd'][:,transectn]
                    
                ###CHECK3: Slope m-direction################################### #For the final bed level
                
            #V    !!! OOK NOG OPLETTEN DAT JE NAAST HET GEDRAAIDE GEVAL NU OOK NOG KAN HEBBEN DAT JE BATHYMETRY GESPIEGELD IS!!!
            
                if c['individualchecks'][l] in ['Slope m-direction']:
                    print('Slope check m-direction')
                    #processing
                    slopem = np.zeros(len(zbEndtransectm))
                    for a in range(n['nx']-1):
                        slopem[a] = (zbEndtransectm[a+1]-zbEndtransectm[a])/n['dx']
                    slopemmean = np.mean(slopem)
                    #checking
                        #LET OP, deze locaties kunnen wat verschillende door de verschillende grex opties, zijn op zich maar 3 cellen dus hoeft geen probleem te zijn
                        # je wilt voor de richting evenwijdig aan de duin eigenlijk ook checken of de slope gemiddeld 0 is (of mag hij ook gemiddeld klein zijn?)
                        
                    if u['tests'][i] in ['pos_x', 'neg_x','hor']: # 'normal'     #OF DEZE TERM NIET MEER GEBRUIKEN??
                        print('ny>nx')  #TEMP
                        if slopemmean==0:
                            check = 0.5
                        else:
                            for b in range(len(c['slopelocations'])):
                                if u['tests'][i] in ['pos_x']:
                                    bb = -1-b       #CONTROLEREN OF DIT ECHT WERKT
                                else:
                                    bb = b
                                if slopem[c['slopelocations'][bb]] > c['slopetheoretical'][bb]*(1+c['slopeconstraint']) or slopem[c['slopelocations'][bb]] < c['slopetheoretical'][bb]*(1-c['slopeconstraint']):
                                    check = 0.5
                                else:
                                    check = 1                   
                    elif u['tests'][i] in ['pos_y','neg_y']: # 'turned'     #OF DEZE TERM NIET MEER GEBRUIKEN??
                        print('ny<nx')  #TEMP
                        if slopemmean==0:           #OF IS DIT EEN TE STRENGE EIS?
                            check = 1
                        else: 
                            check = 0.5
                    print(check) #TEMP
                    
                ###CHECK4: Slope n-direction################################### #For the final bed level
                if c['individualchecks'][l] in ['Slope n-direction']:
                    print('Slope check n-direction') #TEMP
                    if n['ny']>0:                                                                #Otherwise there is no slope to check
                        #processing
                        slopen = np.zeros(len(zbEndtransectn))  #OF DIT OOK IN DE IF-LOOP?
                        
                        for d in range(n['ny']-1):
                            slopen[d] = (zbEndtransectn[d+1]-zbEndtransectn[d])/n['dy']
                        slopenmean = np.mean(slopen)            #OF DIT OOK IN DE IF-LOOP?        
                        #checking
                #V       OOK NOG OPLETTEN BIJ 1D
                        if u['tests'][i] in ['pos_y','neg_y']: # 'turned'     #OF DEZE TERM NIET MEER GEBRUIKEN??
                            print('ny<nx') #TEMP
                            if slopenmean==0:
                                check = 0.5
                            else:
                                for d in range(len(c['slopelocations'])):
                                    if u['tests'][i] in ['pos_y']:
                                        dd = -1-d       #CONTROLEREN OF DIT ECHT WERKT
                                    else:
                                        dd = d
                                    if slopen[c['slopelocations'][dd]] > c['slopetheoretical'][dd]*(1+c['slopeconstraint']) or slopen[c['slopelocations'][dd]] < c['slopetheoretical'][dd]*(1-c['slopeconstraint']):
                                        check = 0.5
                                    else:
                                        check = 1
                        elif u['tests'][i] in ['pos_x', 'neg_x','hor']: # 'normal'     #OF DEZE TERM NIET MEER GEBRUIKEN??
                            print('ny>nx') #TEMP
                            if slopenmean==0:
                                check = 1
                            else: 
                                check = 0.5                
                                        
                        print(check)    #TEMP
                    
                ###CHECK5: MPI m-direction#####################################
                if c['individualchecks'][l] in ['MPI m-direction']:
                    print('MPI m-direction')    #TEMP
                    #processing 
                    
                    #checking
                    
                    #HIER OOK NOG INBOUWEN DAT HIJ CHECKT OF MMPI>1, HIJ MOET ERGENS DAN OOK EEN WARNING GEVEN
                    
                    
                ###CHECK6: MPI n-direction#####################################
                if c['individualchecks'][l] in ['MPI n-direction']:
                    print('MPI n-direction')
                    #processing
                    
                    #checking
                    
                    
            #%%COMPARISON CHECKS###############################################
            for m in range(len(c['comparisonchecks'])):
            
                if c['comparisonchecks'][m] in ['Benchmark']:
                    print('Benchmark')      #ZIE FEEDBACK JUDITH
                    
#%%OUTPUT######################################################################
            
            ###FIGURES###
            #    heb je transectmall nodig voor plots? of kan je binnen elke case elke keer een lijn plotten binnen de figuur?
            #    sowieso nadenken van welke vergelijkingen je plots wilt hebben, wss van dezelfde als dat je comparisonchecks maakt
            
            #            Je zou evt kunnen laten kiezen van welke vergelijking je een plot wilt (of dit iig faciliteren), of alleen van runs
            
            ###MATRICES###
            
            ###VARIABLES###        
            
            ###
                  