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
        check = 0                                                               #check=0 means result is satisfactory
        logger.debug('check= %s', check) 
    else:
        check = 1                                                               #check=1 means test has run but result is unsatisfactory
        logger.debug('check= %s --> mean of delta zb = 0', check)
    return check
    
###CHECK: Mass balance### 
def massbalance(z0, zEnd, dx, dy, massbalancecon):                              #applicable to zs and zb                            
    logger.info('Mass balance is called for') 
    
    #processing
    mass0 = z0.sum() * dx * dy
    massEnd = zEnd.sum() * dx * dy
    massbalance = massEnd - mass0   # WIL JE DIT NOG IN m3/m LATEN ZIEN OF IS DIT NIET RELEVANT MEER?
    logger.debug('massbalance= %s m3', massbalance) 
    
    #checking
    if massbalance > massbalancecon:
        check = 1
        logger.debug('check= %s --> too much mass entering the model', check)              
    elif massbalance < -massbalancecon:
        check = 1
        logger.debug('check= %s --> too much mass leaving the model', check)  
    else:
        check = 0           
    return check, massbalance 

###CHECK: Mass balance in time### 
def massbalance_intime(z, dx, dy, massbalancecon_intime):                       #applicable to zs and zb                  
    logger.info('Mass balance in time is called for') 
    z0 = z[0,:,:]
    massbalance_intime = np.zeros(len(z[:,0,0]))
    
    for i in range(len(massbalance_intime)):
        #processing
        mass0 = z0.sum() * dx * dy
        massuse = z[i,:,:].sum() * dx * dy
        massbalance_intime [i] = massuse - mass0   # WIL JE DIT NOG IN m3/m LATEN ZIEN OF IS DIT NIET RELEVANT MEER?
        
        
        #checking
        if massbalance_intime[i] > massbalancecon_intime:
            check = 1
            logger.debug('check= %s --> too much mass entering the model', check)   
            break           
        elif massbalance_intime[i] < -massbalancecon_intime:
            check = 1
            logger.debug('check= %s --> too much mass leaving the model', check)
            break
        else:
            check = 0 
    logger.debug('massbalance at final timestep= %s m3', massbalance_intime[-1])           
    return check, massbalance_intime    

###CHECK: WAVE BOUNDARY CONDITIONS
def wave_generation(H, ue, ve, ui, vi, xloc, tstart):     
    #processing        
    Hmean = np.mean(H[int(tstart):-1, :, xloc])  #[time, y, x]
    uemean = np.mean(ue[int(tstart):-1, :, xloc]) 
    vemean = np.mean(ve[int(tstart):-1, :, xloc]) 
    if xloc == 0:
        uimean = np.mean(ui[int(tstart):-1, :, xloc])
        vimean = np.mean(vi[int(tstart):-1, :, xloc])
        if uimean == 0:  
            check = 1
            logger.debug('check= %s --> uimean ==0 at xloc= %s', check, xloc)        
        elif vimean == 0:  
            check = 1        
            logger.debug('check= %s --> vimean ==0 at xloc= %s', check, xloc)  
    else:
        logger.debug('ui and vi can only be checked at the offshore boundary grid cells for xloc==0, got xloc= %s', xloc)
        uimean = 0
        vimean = 0
        check = 0
    #checking
    if Hmean == 0:  #or is abs(Hmean) <0.0001 better?
        check = 1
        logger.debug('check= %s --> Hmean ==0 at xloc= %s', check, xloc)        
    elif uemean == 0:  
        check = 1
        logger.debug('check= %s --> uemean ==0 at xloc= %s', check, xloc)        
    elif vemean == 0:  
        check = 1
        logger.debug('check= %s --> vumean ==0 at xloc= %s', check, xloc)                  
    else:
        logger.debug('check= %s --> H, ue, ve, ui and vi are >0 at xloc= %s', xloc)
        check = 0
    return check 
   
###CHECK: Hrms DIFFERENCES ALONG Y AXIS
def n_Hrms(H, ny, tstart, Hrmsconstraint):  
    Hmean_all = np.mean(H[int(tstart):-1,:,:])  #[time, y, x]
    Hmean_ratio = np.zeros(ny)
    for i in range(ny):
        
        Hmean_y = np.mean(H[int(tstart):-1,i,:])
        Hmean_ratio[i] = Hmean_y / Hmean_all
        
    for j in range(ny):
        if Hmean_ratio[j] > (1+Hrmsconstraint): 
            logger.debug('error Hmean >%s', (1+Hrmsconstraint))
            check = 1
            break
            
        elif Hmean_ratio[j] <(1-Hrmsconstraint):
            logger.debug('error Hmean <%s', (1-Hrmsconstraint))
            check = 1
            break   #? --> Je wilt niet dat check weer op 1 wordt gezet als er een goede na een slechte komt
        else:
            check = 0
    
    return check, Hmean_ratio 
        
#%%CHECKS OVER MIDDLE TRANSECT#################################################  

###Making transects###
def midtrans(zb0, zbEnd, ny): #(Middle transect)
    logger.info('Middle transect (midtrans) is called for') 
    
    if ny==0:                                                                   #For 1D cases you do not have to take a transect, also no transect in n-direction
        zb0trans_m = zb0.reshape(-1,1)
        zbEndtrans_m = zbEnd.reshape(-1,1)
        zb0trans_n = 0
        zbEndtrans_n = 0
    else:                                                                       #2D cases
        trans_m = int(round(np.shape(zbEnd)[0]/2))                                   #n-location of central transect in m direction
        trans_n = int(round(np.shape(zbEnd)[1]/2))                                   #m-location of central transect in n direction  
        zb0trans_m = zb0[trans_m, :]    
        zb0trans_n = zb0[:,trans_n]
        zbEndtrans_m = zbEnd[trans_m, :]   
        zbEndtrans_n = zbEnd[:, trans_n]
    return  zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n

###Calculating slopes along transect###
def slope(zbtrans, dd, nd):                                                     #dd = dx or dy, nd = nx or ny
    slp = np.zeros(nd)
    for i in range(nd):
        slp[i] = ((zbtrans[i+1]-zbtrans[i])/dd)  #MOET ABS WEG?????????????
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
            break
        elif slope_m[slploc[b]] < slptheo[b]*(1-slpcon):  
            check = 1
            logger.debug('check= %s --> slope %s < theoretical slope %s', check, slope_m[slploc[b]], slptheo[b] * (1-slpcon))
            break
        else:
            check = 0                   
            logger.debug('check= %s because slope= %s', check, slope_m[slploc[b]])
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
                break
            elif slope_n[slploc[b]] < slptheo[b] * (1 - slpcon):
                check = 1
                logger.debug('check= %s --> slope %s < theoretical slope %s', check, slope_n[slploc[b]] , slptheo[b] * (1 - slpcon))
                break
            else:
                check = 0                   
                logger.debug('check= %s because slope= %s', check, slope_n[slploc[b]])     
    else:
        check = 0 #let 1D cases get a code 0, or is 2 better?
#        raise ValueError('ny>0 expected, got:', ny)
    return check

###CHECK: MPI m-direction### 
def m_mpi(mmpi, zb0, zbEnd, dx, nx, ny, dr, mpicon, mpinr):                     #dr = directory of XBlog, see xb_read_mpi_dims
    logger.info('MPI m-direction is called for')    
    
    if mmpi > 1:
        #processing 
        zb0trans_m, zbEndtrans_m, zb0trans_n, zbEndtrans_n = midtrans(zb0, zbEnd, ny)
        slope_m = slope(zbEndtrans_m, dx, nx)
        mpidim = mpidims(dr)
        if mpidim == 0:
            logger.warning('Something has gone wrong by reading in the XBlog file to read the MPI dimensions') 
            check = 2              
        else:
            locm2 = int(mpidim[:,1][mpinr]) + 0                                     #Note: The overlap of the mpi domains is 3 cells    
            locm1 = locm2 - 1                                                       #You want locm1 to be before the MPI-boundary
            zbEnd_locm2 = zbEndtrans_m[locm2]
            zbEnd_locm1 = zbEndtrans_m[locm1]
            deltareal_m= zbEnd_locm2 - zbEnd_locm1
            deltatheory_m=slope_m[locm1-0] * (locm2 - locm1) * dx #kijken naar die -0
            delta_m=abs(deltareal_m-deltatheory_m)
            logger.debug('locm2= %s, locm1= %s, slope_m[locm1]= %s, deltareal_m= %s and deltatheory_m= %s', locm2, locm1, slope_m[locm1], deltareal_m, deltatheory_m)
    
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
        if mpidim == 0:
            logger.warning('Something has gone wrong by reading in the XBlog file to read the MPI dimensions') 
            check = 2 
        else:               
            locn2 = int(mpidim[:,3][mpinr]) + 0                                             
            locn1 = locn2 - 1                                                       
            zbEnd_locn2 = zbEndtrans_n[locn2]
            zbEnd_locn1 = zbEndtrans_n[locn1]
            deltareal_n= zbEnd_locn2 - zbEnd_locn1
            deltatheory_n=slope_n[locn1-0] * (locn2 - locn1) * dy  #kijken naar die -0
            delta_n=abs(deltareal_n-deltatheory_n)
            logger.debug('locn2= %s, locn1= %s, slope_n[locn1]= %s, deltareal_n= %s and deltatheory_n= %s', locn2, locn1, slope_n[locn1], deltareal_n, deltatheory_n)
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

###CHECK: Benchmark comparison using the RMSE###                    #ZEGGEN DAT JE HIER OP MOET LETTEN MET RICHTING VAN INPUT
def rmse_comp(zbEndbench, zbEnd, ny, rmsecon):
    logger.info('rsme comparison is called for')
    
    #processing 
    diff = np.zeros(len(zbEndbench))
    for i in range(len(zbEnd)):
#        print('i= %s',i)
        diff[i] = zbEnd[i] - zbEndbench[i]
    
#    diff = zbEnd - zbEndbench
#    diffasarray= np.asarray(diff)
    
    
    rmse = (np.sqrt(np.mean((diff)**2)))
#    print('rmse= %s', rmse)
    logger.debug('rmse= %s', rmse)
#    print('zbEnd-zbEndbench is called for: %s', (zbEnd-zbEndbench))  #JE HEBT HIER HET PROBLEEM DAT ZE NIET ALTIJD HETZELFDE GEDRAAID ZIJN!!!
    #checking
    if rmse > rmsecon:
        check = 1
        logger.debug('check= %s --> rmse %s > rmseconstraint %s', check, rmse, rmsecon)
    else:
        check = 0
        logger.debug('check= %s', check)
    return check   


