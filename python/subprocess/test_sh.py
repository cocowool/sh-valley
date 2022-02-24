from os import environ
from subprocess import Popen, STDOUT, PIPE
from sys import stdin

cmd = 'source kubectl.sh; uptime'

p = Popen( cmd, stdin=None, stdout=PIPE, stderr=STDOUT, env=environ, shell=True, close_fds=True, executable='/bin/bash')

# p = Popen(['/bin/bash', '-c', cmd], stdin=None, stdout=PIPE, stderr=STDOUT, env=environ, shell=True, close_fds=True)

while p.poll() is None:
    # time.sleep(0.01)
    if p.stdout:
        print( p.stdout.readline() )

# print(p)