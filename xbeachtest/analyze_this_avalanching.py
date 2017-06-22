#'XBeach Diagnostic Test Model Generator'
# Analysing results of diagnostic tests

#%%GENERAL#####################################################################

import os 
import netCDF4
import logging
import json
import database
import checks
import matplotlib.pyplot as plt

revisionnr = os.getenv('SVN_REVISION')

#Open dictionaries from test-files:
diroutmain = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION')
os.chdir(diroutmain) 

dirout = os.path.join(diroutmain, 'xbeachtest-avalanching-analyze_this.log')  
logging.basicConfig(filename= dirout, format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s', level=logging.DEBUG) #.DEBUG)    
logger = logging.getLogger(__name__)
logger.info('diroutmain= %s', diroutmain)
logger.info('analyze_this_avalanching.py is called for')

with open('dictB_avalanching.txt', 'r') as f:
    b = json.load(f)    
if b == None:
    logger.info('dictionary b is not succesfully read from text file')
else:
    logger.info('dictionary b is read from text file')
    
with open('dictC_avalanching.txt', 'r') as f:
    c = json.load(f)    
if c == None:
    logger.info('dictionary c is not succesfully read from text file')
else:
    logger.info('dictionary c is read from text file')
    
with open('dictU_avalanching.txt', 'r') as f:
    u = json.load(f)    
if u == None:
    logger.info('dictionary u is not succesfully read from text file')
else:
    logger.info('dictionary u is read from text file')
    
#The result per check will be put in a database using:    
database.create_table()
    
#%%READING IN, ANALYSIS AND STORAGE OF MODEL RESULTS###########################

###LOOPS###
logger.info( u['module'])

for i in range(len(u['tests'])):
    
    for j in range(len(u['cases'])):    
        if u['tests'][i] in ['pos_y','neg_y']:   
            runs = ['benchmark','m3n1','m1n3','m3n3']
        else:
            runs = u['runs']
        
        zbEndtrans_m_bench = []
        zbEndtrans_n_bench = []
        
        for k in range(len(runs)):            
            path = os.path.join(diroutmain,
                                u['module'],
                                u['tests'][i],
                                u['cases'][j],
                                runs[k])
            if not os.path.exists(path):
                raise ValueError('There is no path named: %s', path) 
            logger.info(path)
            os.chdir(path)     
            
###READ XBEACH OUTPUT FILES###       
            fname = os.path.join(path , 'xboutput.nc')
            logger.info('read netcdf file from location: %s', fname)
            
            warning = 0
            
            try:
                with netCDF4.Dataset(fname, 'r') as xb:                
                                      
                    # read initial and final topography
                    zb0 = xb.variables['zb'][0,:,:]    
                    zbEnd = xb.variables['zb'][-1,:,:]                
                    
                    # read other parameters
                    parameter = xb.variables['parameter']                     
                    dx = parameter.getncattr('dx')
                    dy = parameter.getncattr('dy')
                    nx = parameter.getncattr('nx')
                    ny = parameter.getncattr('ny')
                    mmpi = parameter.getncattr('mmpi') 
                    nmpi = parameter.getncattr('nmpi') 
            except:
                print('Reading of NetCDF file not possible on location %s', fname)
                logger.warning('Reading of NetCDF file not possibleon location %s', fname)
                warning = 1
            logger.info('Warning= %s', warning)            
            
###PERFORMING CHECKS###            
            checklist = []
            checklist.extend(c['checks_ind'])
            checklist.extend(c['checks_comp'])
            
            for l in range(len(checklist)):
                if warning == 0:
                    if checklist[l] in ['bedlevelchange']:      
                        
                        check = checks.bedlevelchange(zb0, zbEnd)
                        if u['tests'][i] in ['hor']:
                            if check == 1:              #For the horizontal tests it is a satisfactory result if there is no bed level change
                                check = 0
                            else:
                                check = 1
                               
                                
                    elif checklist[l] in ['massbalance']: 
                        check, massbalance = checks.massbalance(zb0, zbEnd, dx, dy, c['massbalancecon'])
                        
                        
                    elif checklist[l] in ['m_slope']:
                        if u['tests'][i] in ['neg_x']:
                            if u['cases'][j] in ['zs0_50']:
                                slptheo = c['slptheo_cross_neg_wet']
                            elif u['cases'][j] in ['zs0_-1']:
                                slptheo = c['slptheo_cross_neg_dry']
                            else:
                                slptheo = c['slptheo_cross_neg_normal']
                                
                        elif u['tests'][i] in ['pos_x']:
                            if u['cases'][j] in ['zs0_50']:
                                slptheo = c['slptheo_cross_pos_wet']
                            elif u['cases'][j] in ['zs0_-1']:
                                slptheo = c['slptheo_cross_pos_dry']
                            else:
                                slptheo = c['slptheo_cross_pos_normal']
                        elif u['tests'][i] in ['pos_y', 'neg_y','hor']: #Hier hoeft niks omgedraaid te worden omdat het om een slope van 0 gaat
                            slptheo = c['slptheo_long'] 
                        logger.debug('slptheo= %s', slptheo)    
                        check = checks.m_slope(zb0, zbEnd, nx, ny, dx, c['slploc'], slptheo, c['slpcon'])   #KIJKEN OF SLPLOC NIET OOK NOG MOET VERANDEREN BIJ POS CASES (niet spiegelen maar andere waarden!!!)
                        
                            
                    elif checklist[l] in ['n_slope']:
                        if runs[k] in ['benchmark','m3n1','m1n3','m3n3']:
                            if u['tests'][i] in ['pos_x', 'neg_x','hor']:   #'hor' should have a slope of 0, which is specified in slptheo_long
                                slptheo = c['slptheo_long']             #Hier hoeft niks omgedraaid te worden omdat het om slopes van 0 gaat
                            elif u['tests'][i] in ['neg_y']:
                                if u['cases'][j] in ['zs0_50']:
                                    slptheo = c['slptheo_cross_neg_wet']
                                elif u['cases'][j] in ['zs0_-1']:
                                    slptheo = c['slptheo_cross_neg_dry']
                                else:
                                    slptheo = c['slptheo_cross_neg_normal']
                                    
                            elif u['tests'][i] in ['pos_y']:
                                if u['cases'][j] in ['zs0_50']:
                                    slptheo = c['slptheo_cross_pos_wet']
                                elif u['cases'][j] in ['zs0_-1']:
                                    slptheo = c['slptheo_cross_pos_dry']
                                else:
                                    slptheo = c['slptheo_cross_pos_normal']
                        else:
                            check = 0
                        logger.debug('slptheo= %s', slptheo)                            
                        check = checks.n_slope(zb0, zbEnd, nx, ny, dy, c['slploc'], slptheo, c['slpcon'])       #check if correctly changed to 'slptheo' instead of 'c['slptheo_long']
                        
                            
                    elif checklist[l] in ['m_mpi']:    
                        if mmpi>1:
                            check = checks.m_mpi(mmpi, zb0, zbEnd, dx, nx, ny, path, c['mpicon'], c['mpinr'])   #dr moet per run veranderen dus daarom is u['diroutmain'] aangepast naar 'path'
                        else:
                            check = 0       #een 0 geven als mmpi = 1
                      
                        
                    elif checklist[l] in ['n_mpi']:    
                        if nmpi>1:
                            check = checks.n_mpi(nmpi, zb0, zbEnd, dy, ny, path, c['mpicon'], c['mpinr'])
                        else:
                            check = 0         #een 0 geven als nmpi = 1
                          
                            
                    elif checklist[l] in ['benchmarkcomp_m']:
                        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = checks.midtrans(zb0, zbEnd, ny)
                        if runs[k] in ['benchmark']:
                            zbEndtrans_m_bench.extend(zbEndtrans_m)
                        check = checks.rmse_comp(zbEndtrans_m_bench,zbEndtrans_m, ny, c['rmsecon'])    
    
                    elif checklist[l] in ['benchmarkcomp_n']:
                        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = checks.midtrans(zb0, zbEnd, ny)
                        if runs[k] in ['benchmark']:                  
                            zbEndtrans_n_bench.extend(zbEndtrans_n)
    
                        if runs[k] in ['m1', 'm3']:
                            check = 0               # code 0 geven want er valt in y-richting niets te checken
                        else:
                            check = checks.rmse_comp(zbEndtrans_n_bench,zbEndtrans_n, ny, c['rmsecon'])   
                        
                    else:
                        check = 2                                                   # check = 2 means that the check is not performed or not finished correctly
                
                elif warning == 1:
                    check = 2
                    print('Performing of checks not possible on location %s', fname)
                    logger.warning('Performing of checks not possible on location %s', fname)
                
                #WRITE CHECK TO DATABASE 
                if checklist[l] in ['massbalance']: 
                     database.massbalance_entry(revisionnr, u['module'], u['tests'][i], u['cases'][j], '', runs[k], checklist[l], check, massbalance)
                     logger.debug('massbalance_entry called for')
                else:
                     database.data_entry(revisionnr, u['module'], u['tests'][i], u['cases'][j], '', runs[k], checklist[l], check)
                     logger.debug('data_entry called for')
                
            #PLOT PROFILES (TEMP)
            if warning == 0:
                logger.debug('Initiate profile plotting sequence')
                zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = checks.midtrans(zb0, zbEnd, ny)
                plt.ioff()
                plt.figure(figsize=(10.0, 5.0))
                if u['tests'][i] in ['pos_x', 'neg_x','hor']:
                    plt.plot(zb0trans_m, label="zb0", color= 'k')
                    plt.plot(zbEndtrans_m, label="zbEnd", color= 'r')
                    
                elif u['tests'][i] in ['pos_y', 'neg_y']:
                    plt.plot(zb0trans_n, label="zb0", color='k')
                    plt.plot(zbEndtrans_n, label="zbEnd", color= 'r')
                    
                    
                plt.title('Bed levels of middle transects perpendicular to the dune')
                plt.xlabel('Grid cells (-)') # in direction perpendicular to dune')
                plt.ylabel('Bed level (m)')
                plt.legend(loc= 4) 
                plt.grid()
                plt.savefig(filename = os.path.join(path , 'profiles-test.png'))
                plt.close()
                logger.debug('End profile plotting sequence')
            elif warning==1:
                print('Performing plotting sequence not possible on location %s', fname)
                logger.warning('Performing plotting sequence not possibleon location %s', fname)