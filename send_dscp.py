import subprocess as sp
import sys
import os
command = sys.argv[1]
print (command + 'ing')

default_base = 'reroute_dscp_63_polatis_tor'
for i in ['1', '3']:
    dir_ = default_base + i
    os.chdir(dir_)
    sp.check_call(['python', command + '.py'])
    os.chdir('..')
