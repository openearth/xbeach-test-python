#'XBeach Diagnostic Test Model Generator'
# Making a database with results of the diagnostic tests

#%%GENERAL#####################################################################

import logging
import os
import sqlite3

logger = logging.getLogger(__name__)
logger.info('checks.py is called for')

diroutmain = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION')
#diroutmain = "P:/xbeach/skillbed/diagnostic/lastrun/"               #TERUGZETTEN!!!
path = os.path.join(diroutmain,'xbeachtest-results.db')            #TERUGZETTEN!!!
conn = sqlite3.connect(path)     #':memory:'  to store in memory
logger.info("Opened database successfully")

db = conn.cursor()

#%%FUNCTIONS REGARDING THE DATABASE############################################

def create_table():
    db.execute('CREATE TABLE IF NOT EXISTS database(modules TEXT, tests TEXT, cases TEXT, runs TEXT, checks TEXT, value REAL, massbalance REAL)')  
             
def data_entry(modules, tests, cases, runs, checks, value):
    db.execute("INSERT INTO database(modules, tests, cases, runs, checks, value) VALUES (?, ?, ?, ?, ?, ?)",  #when using SQL the '?' should maybe be replaced by '%s'
              (modules, tests, cases, runs, checks, value))
    conn.commit()  
    
def massbalance_entry(modules, tests, cases, runs, checks, value, mass):
    db.execute("INSERT INTO database(modules, tests, cases, runs, checks, value, massbalance) VALUES (?, ?, ?, ?, ?, ?, ?)", 
               (modules, tests, cases, runs, checks, value, mass))  
    conn.commit()  
    
def read_ones_from_db():      
    db.execute('SELECT * FROM database WHERE check= 1')   
    ones = dict()
    i=0
    for row in db.fetchall():
        i+=1
        logger.debug('Check=1 for: %s', row)  
        ones['ones', i] = row
    return ones

def read_twos_from_db():       
    db.execute('SELECT * FROM database WHERE check= 2')  
    twos = dict()
    j=0
    for row in db.fetchall():
        j+=1
        logger.debug('Check=2 for: %s', row)
        twos['twos', j] = row
    return twos
    
def close_database():
    db.close()
    conn.close()