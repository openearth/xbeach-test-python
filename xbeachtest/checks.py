#'XBeach Diagnostic Test Model Generator'
# Performing different checks

import numpy as np
import logging
from xb_read_mpi_dims import mpidims
#from analyze_this import c, n, u


logger = logging.getLogger(__name__)
logger.info('checks.py is called for')


#RMSE als vergelijking tussen runs, evt ook tussen tests (de 5 tests min hor)

#%%CHECKS OVER WHOLE GRID##########################################
###CHECK: Bed level change#################################### #Look over whole grid if avalanching happens at all
def bedlevelchange(zb0, zbEnd):    
    logger.info('Bed level check is called for')
    #processing
    zbDelta=np.mean(abs(zbEnd - zb0))
    #checking
    if zbDelta>0:
        check = 1                                                           #Succes
        logger.debug('check= %s', check) 
    else:
        check = 0.5                                                          #Failure
        logger.debug('check= %s --> mean of delta zb = 0', check)
    return check
    
###CHECK: Mass balance########################################
def massbalance(zb0, zbEnd, dx, dy, massbalanceconstraint):         #werkt ook voor de wave test als je zs0 en zsEnd erin stopt???
    logger.info('Mass balance is called for') 
    #processing
    mass0 = zb0.sum() * dx * dy
    massEnd = zbEnd.sum() * dx * dy
#        massDisplaced --> WIL JE DIE NOG BEREKENEN???
    massbalance = massEnd - mass0   # WIL JE DIT NOG IN m3/m LATEN ZIEN OF IS DIT NIET RELEVANT MEER?
#        massbalancepercentage --> WIL JE DIE NOG BEREKENEN???
#        if ny==0:  --> DIE IS MISSCHIEN NIET NODIG DOORDAT NP.SUM OVER JE HELE MATRIX KAN!!! ITT MATLAB
    logger.debug('massbalance= %s m3', massbalance) 
    #checking
    if massbalance > massbalanceconstraint:
        check = 0.5
        logger.debug('check= %s --> too much mass entering the model',check)              
    elif massbalance < massbalanceconstraint:
        check = 0.5
        logger.debug('check= %s --> too much mass leaving the model',check)  
    else:
        check = 1           
    return check, massbalance    
        
#%%CHECKS OVER MIDDLE TRANSECT#####################################  

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
        zb0trans_m = zb0[trans_m, :]    #NODIG? /ER MAAR IN LATEN??
        zb0trans_n = zb0[:,trans_n]
        zbEndtrans_m = zbEnd[trans_m, :]   #ITT MATLAB FILE HET DRAAIEN VAN DE TRANSECT PAS DOEN BIJ DE DAADWERKELIJKE CHECK?
        zbEndtrans_n = zbEnd[:, trans_n]
    return  zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n

###CHECK: Slope m-direction################################### #For the final bed level
def m_slope(zb0, zbEnd, nx, ny, dx, slploc, slptheo, slpcon): 
    logger.info('Slope check m-direction is called for')
    #processing
    zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)
    slope_m = np.zeros(len(zbEndtrans_m))
    #checking
    for i in range(nx-1):
        slope_m[i] = ((zbEndtrans_m[i+1]-zbEndtrans_m[i])/dx)
        
    for b in range(len(slploc)):
        if slope_m[slploc[b]] > slptheo[b]*(1+slpcon):         #KIJKEN OF DIE or WEG MOCHT
            check = 0.5
            logger.debug('check= %s --> slope %s > theoretical slope %s', check, slope_m[slploc[b]] , slptheo[b]*(1+slpcon))
        elif slope_m[slploc[b]] < slptheo[b]*(1-slpcon):  #kijken of slptheo[bb] niet [b] moet zijn, indien dat spiegelen aanstaat
            check = 0.5
            logger.debug('check= %s --> slope %s < theoretical slope %s', check, slope_m[slploc[b]] , slptheo[b]*(1-slpcon))
        else:
            check = 1                   
            logger.debug('check= %s', check)
    return check


###CHECK: Slope n-direction################################### #For the final bed level
def n_slope(zb0, zbEnd, nx, ny, dy, slploc, slptheo, slpcon):               #DE CODE IS NU BIJNA 2X HETZELFDE, KAN DIT NOG KORTER???
    logger.info('Slope check n-direction is called for') 
    if ny>0:                                                                #Otherwise there is no slope to check
        #processing
        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)
        slope_n = np.zeros(len(zbEndtrans_n))  #OF DIT OOK IN DE IF-LOOP?
        #checking
        for d in range(ny-1):
            slope_n[d] = (zbEndtrans_n[d+1]-zbEndtrans_n[d])/dy
                          
        for b in range(len(slploc)):
            if slope_n[slploc[b]] > slptheo[b]*(1+slpcon):         #KIJKEN OF DIE 'or' WEG MOCHT
                check = 0.5
                logger.debug('check= %s --> slope %s > theoretical slope %s', check, slope_n[slploc[b]] , slptheo[b]*(1+slpcon))
            elif slope_n[slploc[b]] < slptheo[b]*(1-slpcon):  #kijken of slptheo[bb] niet [b] moet zijn, indien dat spiegelen aanstaat
                check = 0.5
                logger.debug('check= %s --> slope %s < theoretical slope %s', check, slope_n[slploc[b]] , slptheo[b]*(1-slpcon))
            else:
                check = 1                   
                logger.debug('check= %s', check)     
    else:
        raise ValueError('ny>0 expected, got:', ny)
    return check

###CHECK: MPI m-direction#####################################
def m_mpi(mmpi, zb0, zbEnd, ny):
    logger.info('MPI m-direction is called for')    
    if mmpi > 1:
        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)
        
    #processing 
    
    #checking
    
    #HIER OOK NOG INBOUWEN DAT HIJ CHECKT OF MMPI>1, HIJ MOET ERGENS DAN OOK EEN WARNING GEVEN
    else:
        raise ValueError('mmpi>1 expected, got:', mmpi)
    return check
    
#==============================================================================
# #==============================================================================
# # ###CHECK: MPI n-direction#####################################
#  def n_mpi(nmpi, zb0, zbEnd, ny):
#      logger.info('MPI n-direction is called for')    
#      if nmpi > 1:
#      #processing
#      
#      #checking
#      else:
#          raise ValueError('ny>0 expected, got:', ny)
#      return check
# #==============================================================================
# 
#==============================================================================
###CHECK: WAVE BOUNDARY CONDITIONS
def wave_generation(H, ue, ve, ui, vi, xloc):     #    Kijken of er H, ue, ve, ui, vi aangemaakt worden
    #processing
    
#    xloc = x grid cell waar je wilt kijken of er golven gegenereet worden
#    voor offshore kant doe je hem dan een keer met xloc = 0, en ook een keer met xloc = ... (iets voor de kust)
    
    Hmean = np.mean(H[:,:,xloc])  #[time, y, x]
    uemean = np.mean(ue[:,:,xloc]) #--> kijk hier alleen 
    vemean = np.mean(ve[:,:,xloc])
    if xloc == 0:
        uimean = np.mean(ui[:,:,xloc])
        vimean = np.mean(vi[:,:,xloc])
    else:
        print('ui and vi can only be checked at the offshore boundary grid cells for xloc==0, got xloc= %s', xloc)
        uimean = 0
        vimean = 0
    #checking
    if Hmean == 0:  #of <0.0001 ?
        logger.debug('error Hmean ==0')
        check = 0.5
    elif uemean == 0:  #of <0.0001 ?
        logger.debug('error uemean ==0')
        check = 0.5
    elif vemean == 0:  #of <0.0001 ?
        logger.debug('error vumean ==0')
        check = 0.5
    elif uimean == 0:  #of <0.0001 ?
        logger.debug('error uimean ==0')
        check = 0.5
    elif vimean == 0:  #of <0.0001 ?
        logger.debug('error vimean ==0')
        check = 0.5
    else:
        logger.debug('H, ue, ve, ui and vi are >0 at xloc= %s', xloc)
        check = 1
#    print('Hmean=', Hmean)
#    print('uemean=', uemean)
#    print('vemean=', vemean)
#    print('uimean=', uimean)
#    print('vimean=', vimean)
    
    return check
    
###CHECK: Hrms DIFFERENCES ALONG Y AXIS
def n_Hrms(H, ny):
    
    Hmean_all = np.mean(H[:,:,:])  #[time, y, x]
    Hmean_ratio = np.zeros(len(ny))
    for i in range(ny):
        
        Hmean_y = np.mean(H[:,i,:])
        Hmean_ratio[i] = Hmean_y / Hmean_all
        
        if Hmean_ratio[i] > 0.4: #bijv 0.4 --> Hratioconstraint
            logger.debug('error Hmean >0.4')
            check = 0.5
            
        elif Hmean_ratio[i] <0.2:
            logger.debug('error Hmean >0.4')
            check = 0.5
            
        else:
            check = 1
    
    return check, Hmean_ratio #om te plotten?
    
#%%COMPARISON CHECKS###############################################
#==============================================================================
# for m in range(len(c['comparisonchecks'])):
# 
# if c['comparisonchecks'][m] in ['Benchmark']:
#     print('Benchmark')      #ZIE FEEDBACK JUDITH
#==============================================================================
