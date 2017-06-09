import os
import time


def check_runs():
    # allow the runs to appear in the Linux queue before checking whether they are done
    time.sleep(15)

    maxtime = float(os.getenv('XBEACH_DIAGNOSTIC_MAX_RUNTIME_HRS'));
    starttime = time.mktime(time.localtime());
    currenttime = time.mktime(time.localtime());

    while not is_finished() and currenttime < starttime + maxtime:
        time.sleep(30)
        print('DEBUG: Still running (%s min, max = %s min)'%((currenttime-starttime)/60,maxtime/60))
        currenttime = time.mktime(time.localtime());
        
def is_finished():
    HOSTNAME = os.getenv('CLUSTER_HOSTNAME')
    PORT = int(os.getenv('CLUSTER_PORT'))
    USERNAME = os.getenv('XBEACH_USER')
    PASSWORD = os.getenv('XBEACH_PASS')
    
    finished = True
    
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, PORT, USERNAME, PASSWORD)
    
    project_id = os.getenv('XBEACH_PROJECT_ID_4_LETTER')
    cmd = 'qstat -u %s' % USERNAME
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    for line in stdout.readlines():
        logging.debug(line)
        m = re.match('.*%s.*xbeach\s+r\s+.*|.*%s.*xbeach\s+qw\s+.*' % (project_id,project_id), line)
        if m:
            finished = False
    ssh.close()
    
    return finished
    
if __name__ == '__main__':
    check_runs()
