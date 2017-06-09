#'XBeach Diagnostic Test Model Generator'
# Performing different checks

#%%GENERAL#####################################################################

import logging
import numpy as np
from xb_read_mpi_dims import mpidims

logger = logging.getLogger(__name__)
logger.info('checks.py is called for')

#%%CHECKS OVER WHOLE GRID######################################################

###CHECK: Bed level change###                                                   
def bedlevelchange(zb0, zbEnd):    
    logger.info('Bed level check is called for')
    
    #processing
    zbDelta=np.mean(abs(zbEnd - zb0))
    
    #checking
    if zbDelta > 0:
        check = 0                                                               #check=1 means result is satisfactory
        logger.debug('check= %s', check) 
    else:
        check = 1                                                             #check=0.5 means test has run but result is unsatisfactory
        logger.debug('check= %s --> mean of delta zb = 0', check)
    return check
    
###CHECK: Mass balance### 
def massbalance(zb0, zbEnd, dx, dy, massbalancecon):                            
    logger.info('Mass balance is called for') 
    
    #processing
    mass0 = zb0.sum() * dx * dy
    massEnd = zbEnd.sum() * dx * dy
    massbalance = massEnd - mass0   # WIL JE DIT NOG IN m3/m LATEN ZIEN OF IS DIT NIET RELEVANT MEER?
    logger.debug('massbalance= %s m3', massbalance) 
    
    #checking
    if massbalance > massbalancecon:
        check = 1
        logger.debug('check= %s --> too much mass entering the model', check)              
    elif massbalance < massbalancecon:
        check = 1
        logger.debug('check= %s --> too much mass leaving the model', check)  
    else:
        check = 0           
    return check, massbalance    
        
#%%CHECKS OVER MIDDLE TRANSECT#################################################  

###Making transects###
def midtrans(zb0, zbEnd, ny): #(Middle transect)
    logger.info('Middle transect (midtrans) is called for') 
    
    if ny==0:                                                                   #For 1D cases you do not have to take a transect, also no transect in n-direction
        zb0trans_m = zb0
        zbEndtrans_m = zbEnd
        zb0trans_n = 0
        zbEndtrans_n = 0
    else:                                                                       #2D cases
        trans_m = round(np.shape(zbEnd)[0]/2)                                   #n-location of central transect in m direction
        trans_n = round(np.shape(zbEnd)[1]/2)                                   #m-location of central transect in n direction  
        zb0trans_m = zb0[trans_m, :]    
        zb0trans_n = zb0[:,trans_n]
        zbEndtrans_m = zbEnd[trans_m, :]   
        zbEndtrans_n = zbEnd[:, trans_n]
    return  zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n

###Calculating slopes along transect###
def slope(zbtrans, dd, nd):                                                     #dd = dx or dy, nd = nx or ny
    slp = np.zeros(len(zbtrans))
    for i in range(nd-1):
        slp[i] = ((zbtrans[i+1]-zbtrans[i])/dd)
    return slp

###CHECK: Slope m-direction###                                                  
def m_slope(zb0, zbEnd, nx, ny, dx, slploc, slptheo, slpcon): 
    logger.info('Slope check m-direction is called for')
    
    #processing
    zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)    
    slope_m = slope(zbEndtrans_m, dx, nx) 
    
    #checking    
    for b in range(len(slploc)):
        if slope_m[slploc[b]] > slptheo[b]*(1+slpcon):         
            check = 1
            logger.debug('check= %s --> slope %s > theoretical slope %s', check, slope_m[slploc[b]], slptheo[b] * (1+slpcon))
        elif slope_m[slploc[b]] < slptheo[b]*(1-slpcon):  
            check = 1
            logger.debug('check= %s --> slope %s < theoretical slope %s', check, slope_m[slploc[b]], slptheo[b] * (1-slpcon))
        else:
            check = 0                   
            logger.debug('check= %s', check)
    return check

###CHECK: Slope n-direction###                                                  
def n_slope(zb0, zbEnd, nx, ny, dy, slploc, slptheo, slpcon):               
    logger.info('Slope check n-direction is called for') 
    
    if ny>0:                                                                    #Otherwise there is no slope to check
        #processing
        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)
        slope_n = slope(zbEndtrans_n, dy, ny)
        
        #checking                          
        for b in range(len(slploc)):
            if slope_n[slploc[b]] > slptheo[b] * (1 + slpcon):         
                check = 1
                logger.debug('check= %s --> slope %s > theoretical slope %s', check, slope_n[slploc[b]] , slptheo[b] * (1 + slpcon))
            elif slope_n[slploc[b]] < slptheo[b] * (1 - slpcon):
                check = 1
                logger.debug('check= %s --> slope %s < theoretical slope %s', check, slope_n[slploc[b]] , slptheo[b] * (1 - slpcon))
            else:
                check = 0                   
                logger.debug('check= %s', check)     
    else:
        raise ValueError('ny>0 expected, got:', ny)
    return check

###CHECK: MPI m-direction### 
def m_mpi(mmpi, zb0, zbEnd, dx, nx, ny, dr, mpicon, mpinr):                     #dr = directory of XBlog, see xb_read_mpi_dims
    logger.info('MPI m-direction is called for')    
    
    if mmpi > 1:
        #processing 
        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)
        slope_m = slope(zbEndtrans_m, dx, nx)
        mpidim = mpidims(dr)               
        locm2 = int(mpidim[:,1][mpinr]) + 3                                     #Note: The overlap of the mpi domains is 3 cells    
        locm1 = locm2 - 3                                                       #You want locm1 to be before the MPI-boundary
        zbEnd_locm2 = zbEndtrans_m[locm2]
        zbEnd_locm1 = zbEndtrans_m[locm1]
        deltareal_m= zbEnd_locm2 - zbEnd_locm1
        deltatheory_m=slope_m[locm1-0] * (locm2 - locm1) * dx 
        delta_m=abs(deltareal_m-deltatheory_m)
        
        #checking
        if delta_m > mpicon:
            check = 1
            logger.debug('check= %s --> delta_m %s > mpiconstraint %s', check, delta_m, mpicon)            
        else:
            check = 0
            logger.debug('check= %s', check)                   
    else:
        raise ValueError('mmpi>1 expected, got:', mmpi)
    return check
    
###CHECK: MPI n-direction### 
def n_mpi(nmpi, zb0, zbEnd, dy, ny, dr, mpicon, mpinr):                         
    logger.info('MPI n-direction is called for')    
    
    if nmpi > 1:
        #processing 
        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)
        slope_n = slope(zbEndtrans_n, dy, ny)
        mpidim = mpidims(dr)               
        locn2 = int(mpidim[:,3][mpinr]) + 3                                             
        locn1 = locn2 - 3                                                       
        zbEnd_locn2 = zbEndtrans_n[locn2]
        zbEnd_locn1 = zbEndtrans_n[locn1]
        deltareal_n= zbEnd_locn2 - zbEnd_locn1
        deltatheory_n=slope_n[locn1-0] * (locn2 - locn1) * dy
        delta_n=abs(deltareal_n-deltatheory_n)
        
        #checking
        if delta_n > mpicon:
            check = 1
            logger.debug('check= %s --> delta_n %s > mpiconstraint %s', check, delta_n, mpicon)            
        else:
            check = 0  
            logger.debug('check= %s', check)                 
    else:
        raise ValueError('nmpi>1 expected, got:', nmpi)
    return check

###CHECK: Benchmark comparison using the RMSE### 
def rmse_comp(zbEndbench, zbEnd, ny, rmsecon):
    logger.info('rsme comparison is called for')
    
    #processing 
    rmse = (np.sqrt(np.mean((zbEnd - zbEndbench)**2)))

    #checking
    if rmse > rmsecon:
        check = 1
        logger.debug('check= %s --> rmse %s > rmseconstraint %s', check, rmse, rmsecon)
    else:
        check = 0
        logger.debug('check= %s', check)
    return check   

###CHECK: WAVE BOUNDARY CONDITIONS
def wave_generation(H, ue, ve, ui, vi, xloc):     #    Checken of er H, ue, ve, ui, vi aangemaakt worden
        
#    xloc = x grid cell waar je wilt kijken of er golven gegenereet worden (meestal xloc = 0)
#    voor offshore kant doe je hem dan een keer met xloc = 0, en ook een keer met xloc = ... (iets voor de kust)

    #processing
    Hmean = np.mean(H[:,:,xloc])  #[time, y, x]
    uemean = np.mean(ue[:,:,xloc]) 
    vemean = np.mean(ve[:,:,xloc])
    if xloc == 0:
        uimean = np.mean(ui[:,:,xloc])
        vimean = np.mean(vi[:,:,xloc])
    else:
        logger.debug('ui and vi can only be checked at the offshore boundary grid cells for xloc=0, got xloc= %s', xloc)
        uimean = 0
        vimean = 0
        
    #checking
    if Hmean == 0:  #of overal <0.0001 ?
        logger.debug('error Hmean ==0')
        check = 1
    elif uemean == 0: 
        logger.debug('error uemean ==0')
        check = 1
    elif vemean == 0:  
        logger.debug('error vumean ==0')
        check = 1
    elif uimean == 0: 
        logger.debug('error uimean ==0')
        check = 1
    elif vimean == 0: 
        logger.debug('error vimean ==0')
        check = 1
    else:
        logger.debug('H, ue, ve, ui and vi are >0 at xloc= %s', xloc)
        check = 0
    return check
    
###CHECK: Hrms DIFFERENCES ALONG Y AXIS
def n_Hrms(H, ny):
    
    #processing
    Hmean_all = np.mean(H[:,:,:])                                               #[time, y, x]
    Hmean_ratio = np.zeros(len(ny))
    
    for i in range(ny):        
        Hmean_y = np.mean(H[:,i,:])
        Hmean_ratio[i] = Hmean_y / Hmean_all
        
    #checking
        if Hmean_ratio[i] > 0.4: #bijv 0.4 --> constraint aanmaken
            logger.debug('error Hmean >0.4')
            check = 1            
        elif Hmean_ratio[i] <0.2:
            logger.debug('error Hmean >0.4')
            check = 1            
        else:
            check = 0
    
    return check, Hmean_ratio #Hmean_ratio --> usefull to make a plot of?