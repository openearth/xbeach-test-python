#'XBeach Diagnostic Test Model Generator'
# Reading error codes from database

#%%GENERAL#####################################################################

import database
import json
import os

diroutmain = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION')
#diroutmain = "P:/xbeach/skillbed/diagnostic/lastrun/"
revisionnr = os.getenv('SVN_REVISION')
#revisionnr = 5186 + 0

#%%READING OF RESULTS IN DATABASE##############################################
ones, i = database.read_ones_from_db(revisionnr)   #NOG KIJKEN OF JE DIT ANDERS WILT
if i==0:
    ones[i]= 'The database does not contain ones for this revision'
else:
    ones['0']= 'Apperently some unsatisfactory result ocurred in the diagnostic tests. See also the log file, database and the provided figures and netCDF files in their repective folders'
twos, j = database.read_twos_from_db(revisionnr) 
if j==0:
    twos[j]='The database does not contain twos for this revision'
else:
    twos['0']= 'Apperently some check was not performed correctly. See also the log file and database.'
database.close_database()


#%%WRITE RESULTS TO TXT-FILES##################################################
with open(os.path.join(diroutmain, 'ones.txt'), 'w') as fp:
   json.dump(ones, fp, indent=4) 
      
with open(os.path.join(diroutmain, 'twos.txt'), 'w') as fp:
   json.dump(twos, fp, indent=4)
                
#  if i>0 and j>0:
#    send message