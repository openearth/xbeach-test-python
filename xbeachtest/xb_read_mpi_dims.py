#Python version of Matlab OET script: xb_read_mpi_dims.m
    #Note that the input is not fully checked as in the Matlab script

import numpy as np
import re
import os

def mpidims(dr):
    drXBlog = os.path.join(dr, 'XBlog.txt')
    with open(drXBlog,'r') as f:       
        lines = f.readlines()
    iline = 0
    for i in range(len(lines)):    
        line = lines[i].strip()
        if re.match('^Distribution of matrix on processors', line):  
            iline = i      
            break       
    dim = []
    if iline > 0:  
        iline += 2
        while not re.match('^proc', lines[iline].strip() ):       
            l = lines[iline].strip()
            ll = l.split('   ')
            dim.append(ll)
            dims = np.asarray(dim)
            iline += 1
    else:
        print('The specified log file has no information on mpi domains. Probably it was run on a single core')
        dims = 0           
    
    return dims    