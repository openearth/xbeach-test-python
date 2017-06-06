#'XBeach Diagnostic Test Model Generator'
# Making a database with results of the diagnostic tests

import logging
import sqlite3

logger = logging.getLogger(__name__)
logger.info('checks.py is called for')

conn = sqlite3.connect('xbeach-test-python-results.db')     #':memory:'  to store in memory
logger.info("Opened database successfully")

db = conn.cursor()

def create_table():
    db.execute('CREATE TABLE IF NOT EXISTS database(modules TEXT, tests TEXT, cases TEXT, runs TEXT, checks TEXT, check REAL, massbalance REAL)')
             
 
def data_entry(modules, tests, cases, runs, checks, value):
    db.execute("INSERT INTO database(modules, tests, cases, runs, checks, check) VALUES (?, ?, ?, ?, ?, ?)",  #met SQL is de %s ipv ?
              (modules, tests, cases, runs, checks, value))
    conn.commit()  
    
def massbalance_entry(modules, tests, cases, runs, checks, value, mass):
    db.execute("INSERT INTO database(modules, tests, cases, runs, checks, value, massbalance) VALUES (?, ?, ?, ?, ?, ?,?)", 
               (modules, tests, cases, runs, checks, value, mass))  #mass, ?
    conn.commit()  
    
def read_zeros_from_db():      
    db.execute('SELECT * FROM database WHERE check= 0')   #SELECT value FROM database WHERE value=1'
    zeros = dict()
    i=0
    for row in db.fetchall():
        i+=1
        logger.debug('Check=0 for: %s', row)  
        zeros['zeros', i] = row
    return zeros

def read_halfs_from_db():       
    db.execute('SELECT * FROM database WHERE check= 0.5')   #SELECT value FROM database WHERE value=1'
    halfs = dict()
    j=0
    for row in db.fetchall():
        j+=1
        logger.debug('Check=0.5 for: %s', row)
        halfs['halfs', j] = row
    return halfs

#==============================================================================
# def read_massbalance_from_db(): 
#                                           #Wil je nog zo'n functie??
#     
#     return massbalance
#==============================================================================
    
def close_database():
    db.close()
    conn.close()
    
#OOK DE MASS BALANCE NOG KUNNEN OPSLAAN!              
              
#Gaat wat Bas noemde met die unieke codes automatisch?
