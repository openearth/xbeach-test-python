#!/usr/bin/env python

import os
import paramiko

HOSTNAME = os.getenv('CLUSTER_HOSTNAME')
PORT = int(os.getenv('CLUSTER_PORT'))
USERNAME = os.getenv('XBEACH_USER')
PASSWORD = os.getenv('XBEACH_PASS')
RUNDIR = os.getenv('XBEACH_DIAGNOSTIC_RUNLOCATION_UNIX')

def runall():
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, PORT, USERNAME, PASSWORD)
    cmd = 'find %s -name run.sh | awk \'{print "cd %s && dos2unix \\""$1"\\" && qsub \\""$1"\\" && cd -"}\' | /bin/bash' % RUNDIR
    print(cmd) #"##teamcity[message '%s']" % cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    for line in stdout.readlines():
        print(line) #"##teamcity[message '%s']" % line)
    ssh.close()

    
if __name__ == '__main__':
    runall()
