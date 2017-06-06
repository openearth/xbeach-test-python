#Python version of Matlab OET script: xb_read_mpi_dims.m
#Note that the input is not fully checked as in the Matlab script

import re
import numpy as np
    
#==============================================================================
# Input:
#    dr  = Directory where the XBlog file resides
# 
#    Output:
#    dims = the n * 5 matrix included in the XBlog file that describes the
#            mpi domain dimensions in which:
#                First column:  domain number
#                Second column: position of the left boundary in m direction (cross-shore)
#                Third column:  Length of the domain in m direction (cross-shore)
#                Fourth column: position of upper boundary in n direction (alongshore)
#                Third column:  Length of the domain in n direction (alongshore)
# 
#            For example:
#                     0    1  107    1   63
#                     1  106  106    1   63
#                     2  210  106    1   63
#                     3    1  107   62   62
#                     4  106  106   62   62
#                     5  210  106   62   62
# 
#==============================================================================

def mpidims(dr):
    with open(dr+'XBlog.txt','r') as f:       
        lines = f.readlines()#[31:]
    
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