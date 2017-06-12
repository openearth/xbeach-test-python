import re
import os
import paramiko
import logging

HOSTNAME = os.getenv('CLUSTER_HOSTNAME')
PORT = int(os.getenv('CLUSTER_PORT'))
USERNAME = os.getenv('XBEACH_USER')
PASSWORD = os.getenv('XBEACH_PASS')
project_id = os.getenv('XBEACH_PROJECT_ID_4_LETTER')

def clean_cluster_jobs():
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, PORT, USERNAME, PASSWORD)
    print(ssh)
    cmd = 'qstat -u %s' % USERNAME
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    for line in stdout.readlines():
        print(line)
        logging.debug(line)
        m = re.match('.*%s.*xbeach\s+E\s+.*|.*%s.*xbeach\s+dt\s+.*|.*%s.*xbeach\s+t\s+.*|.*%s.*xbeach\s+Eqw\s+.*|.*%s.*xbeach\s+dr\s+.*|.*%s.*xbeach\s+r\s+.*|.*%s.*xbeach\s+qw\s+.*' % (project_id,project_id,project_id,project_id,project_id,project_id,project_id), line)
        if m:
            m2 = re.search('\s+(\d+)\s+0\.',line)
            jobid = int(m2.group(1))
            if not jobid:
                logging.info("No jobs found.")
            else:
                cmd_del = 'qdel -f %d' % (jobid)
                stdin_del, stdout_del, stderr_del = ssh.exec_command(cmd_del, timeout=5)
                for li in stdout_del.readlines():
                    print(li)
                    logging.info("%s" % li)
                logging.info("Deleting job: %d" % jobid)
    ssh.close()
    
if __name__ == '__main__':
    clean_cluster_jobs()
