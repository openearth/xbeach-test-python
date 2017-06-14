#'XBeach Diagnostic Test Model Generator'
# Analysing results of diagnostic tests

#%%GENERAL#####################################################################

import os 
import netCDF4
import logging
import json
import database
import checks

#Open dictionaries from test-files:
diroutmain = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION')
os.chdir(diroutmain) 

dirout = os.path.join(diroutmain, 'xbeachtest-avalanching-analyze_this.log')  
logging.basicConfig(filename= dirout, format='%(asctime)-15s %(name)-8s %(levelname)-8s %(message)s', level=logging.DEBUG) #.DEBUG)    
logger = logging.getLogger(__name__)
logger.info('diroutmain= %s', diroutmain)
logger.info('analyze_this.py is called for')

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
#        zbEndtrans_m_comp = []
        zbEndtrans_n_bench = []
#        zbEndtrans_n_comp = []
        
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
                        
###PERFORMING CHECKS###            
            checklist = []
            checklist.extend(c['checks_ind'])
            checklist.extend(c['checks_comp'])
            
            for l in range(len(checklist)):
                if checklist[l] in ['bedlevelchange']:      
                    check = checks.bedlevelchange(zb0, zbEnd)
                    
                elif checklist[l] in ['massbalance']: 
                    check, massbalance = checks.massbalance(zb0, zbEnd, dx, dy, c['massbalancecon'])
                    
                elif checklist[l] in ['m_slope']:
                    if u['tests'][i] in ['pos_x', 'neg_x']:
                        slptheo = c['slptheo_cross']
                    elif u['tests'][i] in ['pos_y', 'neg_y','hor']:
                        slptheo = c['slptheo_long']
                    check = checks.m_slope(zb0, zbEnd, nx, ny, dx, c['slploc'], slptheo, c['slpcon'])
                    
                elif checklist[l] in ['n_slope']:
                    if u['tests'][i] in ['pos_x', 'neg_x']:
                        slptheo = c['slptheo_long']
                    elif u['tests'][i] in ['pos_y', 'neg_y','hor']:
                        slptheo = c['slptheo_cross']
                    check = checks.n_slope(zb0, zbEnd, nx, ny, dy, c['slploc'], slptheo, c['slpcon'])       #check if correctly changed to 'slptheo' instead of 'c['slptheo_long']
                    
                elif checklist[l] in ['m_mpi']:    
                    if mmpi>1:
                        check = checks.m_mpi(mmpi, zb0, zbEnd, dx, nx, ny, path, c['mpicon'], c['mpinr'])   #dr moet per run veranderen dus daarom is u['diroutmain'] aangepast naar 'path'
                        
                elif checklist[l] in ['n_mpi']:    
                    if nmpi>1:
                        check = checks.n_mpi(nmpi, zb0, zbEnd, dy, ny, path, c['mpicon'], c['mpinr'])
                        
                elif checklist[l] in ['benchmarkcomp_m']:
                    zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = checks.midtrans(zb0, zbEnd, ny)
#                    print('First zbEndtrans_m_list= %s', zbEndtrans_m_list)
                    if runs[k] in ['benchmark']:
                        zbEndtrans_m_bench.extend(zbEndtrans_m)
#                    zbEndtrans_m_comp.extend(zbEndtrans_m)
                    
#                    print('zbEndtrans_m_list= %s', zbEndtrans_m_list)                   
#                    print('After extending zbEndtrans_m_list= %s', zbEndtrans_m_list)
#                    print('zbEndtrans_m= %s', zbEndtrans_m)
                    check = checks.rmse_comp(zbEndtrans_m_bench,zbEndtrans_m, ny, c['rmsecon'])     #zbEndtrans_m instead of zbEndtrans_m_list[k]
#HIER GOED OPLETTEN DAT DE VORMEN WEL ECHT HETZELFDE ZIJN, BELANGRIJK VOOR .EXTEND EN RMSE_COMP
                elif checklist[l] in ['benchmarkcomp_n']:
                    zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = checks.midtrans(zb0, zbEnd, ny)
#                    print('First zbEndtrans_n_list= %s', zbEndtrans_n_list)
                    if runs[k] in ['benchmark']:                  
                        zbEndtrans_n_bench.extend(zbEndtrans_n)
#                    zbEndtrans_n_comp.extend(zbEndtrans_n)
#                    print('zbEndtrans_n_list= %s', zbEndtrans_n_list)
                    if runs[k] in ['m1', 'm3']:
                        check = 0               # code 0 geven want er valt in y-richting niets te checken
                    else:
                        check = checks.rmse_comp(zbEndtrans_n_bench,zbEndtrans_n, ny, c['rmsecon'])   
                    
                else:
                    check = 2
                
                #WRITE CHECK TO DATABASE 
                if checklist[l] in ['massbalance']: 
                     database.massbalance_entry(u['module'], u['tests'][i], u['cases'][j], runs[k], checklist[l], check, massbalance)
                     logger.debug('massbalance_entry called for')
                else:
                     database.data_entry(u['module'], u['tests'][i], u['cases'][j], runs[k], checklist[l], check)
                     logger.debug('data_entry called for')
               
#%%OUTPUT######################################################################
      
#outside loop  -> the results should send error messages to the person responsible
#--> This can also be done in a seperate script (especially if tests for other modules are added to the same database)
#==============================================================================
# zeros = database.read_zeros_from_db()   #NOG KIJKEN OF JE DIT ANDERS WILT
# 
# halfs = database.read_halfs_from_db() 
# 
# #massbalance = database.read_massbalance_from_db()  --> evt nog maken
# 
# database.close_database()
# 
#==============================================================================