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
#revisionnr = 5186 + 1

#Open dictionaries from test-files:
diroutmain = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION')
#diroutmain = "P:/xbeach/skillbed/diagnostic/lastrun/"
os.chdir(diroutmain) 

dirout = os.path.join(diroutmain, 'xbeachtest-waves-analyze_this.log')  
#logging.basicConfig(filename= dirout, format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s', level=logging.DEBUG) #.DEBUG)    
logger = logging.getLogger(__name__)
logger.info('diroutmain= %s', diroutmain)
logger.info('analyze_this_waves.py is called for')

with open('dictB_waves.txt', 'r') as f:
    b = json.load(f)    
if b == None:
    logger.info('dictionary b is not succesfully read from text file')
else:
    logger.info('dictionary b is read from text file')
    
with open('dictC_waves.txt', 'r') as f:
    c = json.load(f)    
if c == None:
    logger.info('dictionary c is not succesfully read from text file')
else:
    logger.info('dictionary c is read from text file')
    
with open('dictU_waves.txt', 'r') as f:
    u = json.load(f)    
if u == None:
    logger.info('dictionary u is not succesfully read from text file')
else:
    logger.info('dictionary u is read from text file')
    
with open('dictW_waves.txt', 'r') as f:
    w = json.load(f)    
if w == None:
    logger.info('dictionary w is not succesfully read from text file')
else:
    logger.info('dictionary w is read from text file')
    
#The result per check will be put in a database using:    
database.create_table()                                         ###TESTEN OF DIT GOED GAAT OMDAT JE AL EEN TABEL HEBT AANGEMAAKT... OF KAN HET DAAROM WEG ZOLANG AVALANCHING ANALYSE MAAR EERST GEDRAAID WORDT?
    
#%%READING IN, ANALYSIS AND STORAGE OF MODEL RESULTS###########################

###LOOPS###
logger.info(u['module'])

for i in range(len(u['tests'])):
    
    for j in range(len(u['cases'])):    
        
        for jj in range(len(u['subcases'])):    
            logger.info(u['subcases'][jj])
            
            zbEndtrans_m_bench = []
            zbEndtrans_n_bench = []
        
            for k in range(len(u['runs'])):            
                path = os.path.join(diroutmain,
                                    u['module'],
                                    u['tests'][i],
                                    u['cases'][j],
                                    u['subcases'][jj],
                                    u['runs'][k])
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
                                          
                        # read initial and final bed and surface levels
                        zb0 = xb.variables['zb'][0,:,:]    
                        zbEnd = xb.variables['zb'][-1,:,:]
                        zs = xb.variables['zs'][:,:,:]
                        zs0 = xb.variables['zs'][0,:,:]    
                        zsEnd = xb.variables['zs'][-1,:,:] 
                        
                        # read wave and flow variables
                        H = xb.variables['H'][:,:,:]
                        ue = xb.variables['ue'][:,:,:]
                        ve = xb.variables['ve'][:,:,:]
                        ui = xb.variables['ui'][:,:,:]
                        vi = xb.variables['vi'][:,:,:]
                        
                        # read other parameters
                        parameter = xb.variables['parameter']                     
                        dx = parameter.getncattr('dx')
                        dy = parameter.getncattr('dy')
                        nx = parameter.getncattr('nx')
                        ny = parameter.getncattr('ny')
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
                        if checklist[l] in ['bedlevelchange_zb']:                              
                            check_zb = checks.bedlevelchange(zb0, zbEnd)                        
                            if check_zb == 1:              #For the the bedlevel it is a satisfactory result if there is no bed level change because these processes are turned off
                                check = 0
                            else:
                                check = 1
                                   
                        elif checklist[l] in ['bedlevelchange_zs']:      #now if there is no difference in zs it is an unsatisfactory result                        
                            check = checks.bedlevelchange(zs0, zsEnd)  
                            
                        elif checklist[l] in ['massbalance_zb']: 
                            check, massbalance = checks.massbalance(zb0, zbEnd, dx, dy, c['massbalancecon_zb'])
                            
                        elif checklist[l] in ['massbalance_zs']:
                            check, massbalance = checks.massbalance(zs0, zsEnd, dx, dy, c['massbalancecon_zs'])  
                        
                        elif checklist[l] in ['massbalance_intime']:
                            check, massbalance_intime = checks.massbalance_intime(zs, dx, dy, c['massbalancecon_intime'])
                            
                        elif checklist[l] in ['wave_generation_offshore']:
                            check = checks.wave_generation(H, ue, ve, ui, vi, c['xloc1'], c['tstart'])
                            
                        elif checklist[l] in ['wave_generation_coast']:
                            check = checks.wave_generation(H, ue, ve, ui, vi, c['xloc2'], c['tstart']) 
                            
                        elif checklist[l] in ['n_Hrms']:
                            check, Hmean_ratio = checks.n_Hrms(H, ny, c['tstart'], c['Hrmsconstraint'])
    #==============================================================================
    #                     elif checklist[l] in ['benchmarkcomp_m']:
    #                         zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = checks.midtrans(zb0, zbEnd, ny)
    #                         if u['runs'][k] in ['benchmark']:
    #                             zbEndtrans_m_bench.extend(zbEndtrans_m)
    #                         check = checks.rmse_comp(zbEndtrans_m_bench,zbEndtrans_m, ny, c['rmsecon'])    
    #     
    #                     elif checklist[l] in ['benchmarkcomp_n']:
    #                         zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = checks.midtrans(zb0, zbEnd, ny)
    #                         if runs[k] in ['benchmark']:                  
    #                             zbEndtrans_n_bench.extend(zbEndtrans_n)
    #     
    #                         if u['runs'][k] in ['m1', 'm3']:
    #                             check = 0               # code 0 geven want er valt in y-richting niets te checken
    #                         else:
    #                             check = checks.rmse_comp(zbEndtrans_n_bench,zbEndtrans_n, ny, c['rmsecon'])   
    #==============================================================================                        
                        else:
                            check = 2                                                   # check = 2 means that the check is not performed or not finished correctly
                
                    elif warning == 1:
                        check = 2
                        print('Performing of checks not possible on location %s', fname)
                        logger.warning('Performing of checks not possible on location %s', fname)
                        
                    #WRITE CHECK TO DATABASE 
                    if checklist[l] in ['massbalance_zs','massbalance_zb']: 
                         database.massbalance_entry(revisionnr, u['module'], u['tests'][i], u['cases'][j], u['subcases'][jj], u['runs'][k], checklist[l], check, massbalance)
                         logger.debug('massbalance_entry called for')
                    else:
                         database.data_entry(revisionnr, u['module'], u['tests'][i], u['cases'][j], u['subcases'][jj], u['runs'][k], checklist[l], check)
                         logger.debug('data_entry called for')
                    
                #PLOT PROFILES (TEMP)   
                if warning == 0:
                    logger.debug('Initiate profile plotting sequence')
                    plt.ioff()
                    plt.figure(figsize=(10.0, 5.0))
                    plt.plot(Hmean_ratio)                
                    plt.title('Ratio of mean Hrms along transect in x-direction and mean Hrms over the whole grid, after spinup time')
                    plt.xlabel('Grid cells along y-axis(-)')
                    plt.ylabel('Ratio of mean(Hrms(y))/mean(Hrms)')
                    plt.grid()
                    plt.savefig(filename = os.path.join(path , 'Hrms_ratio.png'))
                    plt.close()
                    
                    plt.figure(figsize=(10.0, 5.0))
                    plt.imshow(H[-1,:,:])
                    plt.gca().invert_yaxis()
                    plt.title('Hrms(m) on last timestep')
                    plt.xlabel('Grid cells along x-axis(-)')
                    plt.ylabel('Grid cells along y-axis(-)')
                    plt.colorbar()
                    plt.savefig(filename = os.path.join(path , 'Hrms_end.png'))
                    plt.close()
                    
                    check, massbalance_intime = checks.massbalance_intime(zs, dx, dy, c['massbalancecon_intime'])
                    plt.figure(figsize=(10.0, 5.0))
                    plt.plot(massbalance_intime)
                    plt.title('Mass balance of zs in time wrt initial water level')
                    plt.xlabel('time(s) x10')
                    plt.ylabel('Mass balance of zs(m3)')
                    plt.grid()
                    plt.savefig(filename = os.path.join(path , 'massbalance_zs_intime.png'))
                    plt.close()
                    logger.debug('End profile plotting sequence')                
                elif warning==1:
                    print('Performing plotting sequence not possible on location %s', fname)
                    logger.warning('Performing plotting sequence not possibleon location %s', fname)