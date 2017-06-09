#!/usr/bin/env python

import os
import paramiko

HOSTNAME = 'h6'
PORT = 22
USERNAME = os.getenv('XBEACH_USER')
PASSWORD = os.getenv('XBEACH_PASS')
RUNDIR = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION_UNIX')

def runall():
    s = paramiko.SSHClient()
    s.load_system_host_keys()
    s.connect(HOSTNAME, PORT, USERNAME, PASSWORD)
    cmd = 'find %s -name run.sh | awk \'{print "qsub \""$1"\""}\' | /bin/bash' % RUNDIR
    print "##teamcity[message '%s']" % cmd
    stdin, stdout, stderr = s.exec_command(cmd)
    for line in stdout.readlines():
        print "##teamcity[message '%s']" % line
    s.close()

    
if __name__ == "main":
    runall()
