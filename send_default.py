import subprocess as sp
import sys
import os
command = sys.argv[1]
print (command + 'ing')

default_base = 'two_way_l2_tor'
for i in ['1', '2', '3']:
    dir_ = default_base + i
    os.chdir(dir_)
    sp.check_call(['python', command + '.py'])
    os.chdir('..')
