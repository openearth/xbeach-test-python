#Python version of Matlab OET script: xb_read_mpi_dims.m
    #Note that the input is not fully checked as in the Matlab script

import numpy as np
import re

def mpidims(dr):
    with open(dr+'XBlog.txt','r') as f:       
        lines = f.readlines()
    
    for i in range(len(lines)):    
        line = lines[i].strip()
        if re.match('^Distribution of matrix on processors', line):  
            iline = i      
            break       
    if iline:
        iline += 2
    else:
        raise ValueError('The specified log file has no information on mpi domains. Probably it was run on a single core')
            
    dim = []
    
    while not re.match('^proc', lines[iline].strip() ):       
        l = lines[iline].strip()
        ll = l.split('   ')
        dim.append(ll)
        dims  =np.asarray(dim)
        iline += 1
        
    return dims    