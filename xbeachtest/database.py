#'XBeach Diagnostic Test Model Generator'
# Making a database with results of the diagnostic tests

#%%GENERAL#####################################################################

import logging
import os
import sqlite3

logger = logging.getLogger(__name__)
logger.info('checks.py is called for')

diroutmain = os.getenv('XBEACH_DIAGNOSTIC')
#diroutmain = "P:/xbeach/skillbed/diagnostic/"               #TERUGZETTEN!!!
path = os.path.join(diroutmain,'xbeachtest-results.db')            #-test- TERUGZETTEN!!!
conn = sqlite3.connect(path)     #':memory:'  to store in memory
logger.info("Opened database successfully")

db = conn.cursor()

#%%FUNCTIONS REGARDING THE DATABASE############################################

def create_table():
    db.execute('CREATE TABLE IF NOT EXISTS XBdiagnostic(revision REAL, modules TEXT, tests TEXT, cases TEXT, subcases TEXT, runs TEXT, checks TEXT, value REAL, massbalance REAL)')  
             
def data_entry(revision, modules, tests, cases, subcases, runs, checks, value):
    db.execute("INSERT INTO XBdiagnostic(revision, modules, tests, cases, subcases, runs, checks, value) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",  #when using SQL the '?' should maybe be replaced by '%s'
              (revision, modules, tests, cases, subcases, runs, checks, value))
    conn.commit()  
    
def massbalance_entry(revision, modules, tests, cases, subcases, runs, checks, value, mass):
    db.execute("INSERT INTO XBdiagnostic(revision, modules, tests, cases, subcases, runs, checks, value, massbalance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
               (revision, modules, tests, cases, subcases, runs, checks, value, mass))  
    conn.commit()  
    
def read_ones_from_db(revisionnr):      
    logger.debug('chosen revisionnr= %s', revisionnr)
    db.execute('SELECT * FROM XBdiagnostic WHERE revision= (?) AND value= (?)', (float(revisionnr),float(1)))   ##AANPASSEN --> JE WILT ALLEEN KIJKEN VOOR HET REVISIENUMMER DAT JE DRAAIT!!!
    ones = dict()
    i=0
    for row in db.fetchall():
        i+=1
        logger.debug('Check=1 for: %s', row)  
        ones[i] = row#str(row)
    return ones, i

def read_twos_from_db(revisionnr):       
    logger.debug('chosen revisionnr= %s', revisionnr)
    db.execute('SELECT * FROM XBdiagnostic WHERE revision= (?) AND value= (?)', (float(revisionnr),float(2)))  #WHERE revision = revisionnr and value= 2
    twos = dict()
    j=0
    for row in db.fetchall():
        j+=1
        logger.debug('Check=2 for: %s', row)
        twos[j] = row#str(row)
    return twos, j
    
def close_database():
    db.close()
    conn.close()