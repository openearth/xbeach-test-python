#!/usr/bin/env python

import os
import paramiko

HOSTNAME = 'h6'
PORT = 22
USERNAME = os.getenv('XBEACH_USER')
PASSWORD = os.getenv('XBEACH_PASS')
RUNDIR = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION_UNIX')

def runall():
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, PORT, USERNAME, PASSWORD)
    cmd = 'find %s -name run.sh | awk \'{print "qsub \""$1"\""}\' | /bin/bash' % RUNDIR
    print("##teamcity[message '%s']" % cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    for line in stdout.readlines():
        print("##teamcity[message '%s']" % line)
    ssh.close()

    
if __name__ == "__main__':
    runall()
