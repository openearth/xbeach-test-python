#'XBeach Diagnostic Test Model Generator'
# Analysing results of diagnostic tests


#%%GENERAL#####################################################################

import numpy as np
import os 
import netCDF4
import logging
import json
import database
import checks

logger = logging.getLogger(__name__)
logger.info('analyze_this.py is called for')

#heb je ook weer mpidims = xb_read_mpi_dims(dirin) (van Matlab) nodig?
    
with open('Bdictionary.txt', 'r') as f:
    b = json.load(f)    
if b == None:
    logger.info('dictionary b is not succesfully read from text file')
else:
    logger.info('dictionary b is read from text file')
    
with open('Cdictionary.txt', 'r') as f:
    c = json.load(f)    
if c == None:
    logger.info('dictionary c is not succesfully read from text file')
else:
    logger.info('dictionary c is read from text file')
    
with open('Udictionary.txt', 'r') as f:
    u = json.load(f)    
if u == None:
    logger.info('dictionary u is not succesfully read from text file')
else:
    logger.info('dictionary u is read from text file')
    

#PUTTING THE RESULT PER CHECK IN THE DATABASE:    
database.create_table()
    
#%%LOOPS
logger.info( u['module'])

for i in range(len(u['tests'])):
    
    for j in range(len(u['cases'])):    
        if u['tests'][i] in ['pos_y','neg_y']:   
            runs = ['benchmark','m3n1','m1n3','m3n3']
        else:
            runs = u['runs']
            
        for k in range(len(runs)):            
            path = (u['diroutmain']   + u['module'] + '/' + u['tests'][i] + '/' + u['cases'][j] + '/' + runs[k] + '/')
            logger.info(path)
            os.chdir(path) 
      
            #%%READ XBEACH OUTPUT FILES########################################     
            fname = 'C:/Users/Leijnse/Desktop/Checkouts/openearth/xbeach-test-python/xbeachtest/xboutput.nc'
            #            fname = path + "xboutput.nc" 
            
            with netCDF4.Dataset(fname, 'r') as xb:
                
                parameter = xb.variables['parameter']            
                # read initial and final topography
                zb0 = xb.variables['zb'][0,:,:]    
                zbEnd = xb.variables['zb'][-1,:,:]                
                
                # read other parameters                   
                dx = parameter.getncattr('dx')
                dy = parameter.getncattr('dy')
                nx = parameter.getncattr('nx')
                ny = parameter.getncattr('ny')
                mpi = parameter.getncattr('mpiboundary_str')    #NOG NODIG???
                mmpi = parameter.getncattr('mmpi') 
                nmpi = parameter.getncattr('nmpi') 
            
            #==================================================================
            #     JE WILT EIGENLIJK NOG IETS DAT WERKT ALS xb_read_mpi_dims.m
            #       dit kan dan binnen de code of als extra .py bij GitHub
            #==================================================================
            
            
            #%%##############################################
            checklist = []
            checklist.extend(c['individualchecks'])
            checklist.extend(c['comparisonchecks'])
            for l in range(len(checklist)):
                if checklist[l] in ['bedlevelchange']:      
                    check = checks.bedlevelchange(zb0, zbEnd)
                    
                if checklist[l] in ['massbalance']: 
                    check, massbalance = checks.massbalance(zb0, zbEnd, dx, dy, c['massbalanceconstraint'])
                    
                if checklist[l] in ['m_slope']:
                    if u['tests'][i] in ['pos_x', 'neg_x']:
                        slptheo = c['slptheo_cross']
                    elif u['tests'][i] in ['pos_y', 'neg_y','hor']:
                        slptheo = c['slptheo_long']
                    check = checks.m_slope(zb0, zbEnd, nx, ny, dx, c['slploc'], slptheo , c['slpcon'])
                    
                if checklist[l] in ['n_slope']:
                    if u['tests'][i] in ['pos_x', 'neg_x']:
                        slptheo = c['slptheo_long']
                    elif u['tests'][i] in ['pos_y', 'neg_y','hor']:
                        slptheo = c['slptheo_cross']
                    check = checks.n_slope(zb0, zbEnd, nx, ny, dy, c['slploc'], c['slptheo_long'], c['slpcon'])
                
                #WRITE CHECK TO DATABASE
                database.data_entry('avalanching',u['tests'][i], u['cases'][j], runs[k], checklist[l], check)    #CONTROLEREN OF DIT GOED GAAT MET EEN VERSCHILLENDE LENGTE VAN RUN!!!
                #HIER TYPEN DAT MASS BALANCE MEEGESCHREVEN WORDT INDIEN GETAL AANWEZIG, OF ALTIJD?
    
      
#%%OUTPUT######################################################################
      
#outside loop  -> the results should send error messages to the person responsible
zeros = database.read_zeros_from_db()   #NOG KIJKEN OF JE DIT ANDERS WILT

halfs = database.read_halfs_from_db() 

database.close_database()


