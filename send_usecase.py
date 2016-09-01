import subprocess as sp
import sys
import os
command = sys.argv[1]
print (command + 'ing')
usecase = sys.argv[2]
print ('use case ' + str(usecase))

if usecase == '0':
    base = 'two_way_l2_tor'
elif usecase == '1':
    base = 'dscp_to_optical_private_tor'
elif usecase == '2':
    base = 'dscp_to_optical_shared_tor'
elif usecase == '3':
    base = 'dscp_to_optical_all_tor'
elif usecase == '4':
    base = 'dscp_to_optical_node1_tor'
for i in ['1', '2', '3']:
    dir_ = base + i
    try:
        os.chdir(dir_)
    except OSError:
        print ('Warning! ' + dir_ + ' does not exist')
    else:
        sp.check_call(['python', command + '.py'])
        os.chdir('..')
