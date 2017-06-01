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
    db.execute('CREATE TABLE IF NOT EXISTS database(modules TEXT, tests TEXT, cases TEXT, runs TEXT, checks TEXT, value REAL)')
             
 
def data_entry(modules, tests, cases, runs, checks, value):
    db.execute("INSERT INTO database(modules, tests, cases, runs, checks, value) VALUES (?, ?, ?, ?, ?, ?)",  #met SQL is de %s ipv ?
              (modules, tests, cases, runs, checks, value))
    conn.commit()  
    
def read_zeros_from_db():      
    db.execute('SELECT * FROM database WHERE value= 0')   #SELECT value FROM database WHERE value=1'
    zeros = []
    for row in db.fetchall():
        logger.debug('Check=0 for: %s', row)  
        zeros.extend(row)
    return zeros

def read_halfs_from_db():       
    db.execute('SELECT * FROM database WHERE value= 0.5')   #SELECT value FROM database WHERE value=1'
    halfs = []
    for row in db.fetchall():
        logger.debug('Check=0.5 for: %s', row)
        halfs.extend(row)
    return halfs
    
def close_database():
    db.close()
    conn.close()
    
#OOK DE MASS BALANCE NOG KUNNEN OPSLAAN!              
              
#Gaat wat Bas noemde met die unieke codes automatisch?
