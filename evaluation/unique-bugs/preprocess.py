
import os
import re
from sys import argv
import time


assert(len(argv) == 2)
dir = argv[1] 

coverage_dir = os.path.join(dir, "coverage")

coverage_files = os.listdir(coverage_dir)

time_str = re.findall(r'\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2}', coverage_files[0]) 

assert(len(time_str) == 1)

init_time = time.mktime(time.strptime(time_str[0], "%Y-%m-%d-%H:%M:%S"))

bisect_dir = os.path.join(dir, "bisection")
for f in os.listdir(bisect_dir):
    if "bisection.log" in f:
        bisect_path = os.path.join(bisect_dir, f)
print(bisect_path)
assert(os.path.isfile(bisect_path) == True)

time2fix = []
with open(bisect_path, 'r') as of:
    line = of.readline()
    while(line):
        if "fixed" not in line:
            print(line)
            line = of.readline()
            continue
        line_list = line.split(": ")
        file_name = line_list[0]
        date_time = file_name[:19]
        parsed_time = time.strptime(date_time, "%Y-%m-%d-%H:%M:%S")

        fix_info = line_list[1]
        if "Is fixed" in fix_info:
            fix = fix_info.split('\n')[0].split(' ')[-1]
        else:
            fix = None
        
        if "crash" in file_name:
            crash = True
        else:
            crash = False
        time2fix.append([parsed_time, fix, crash])

        line = of.readline()

sorted_time2fix = sorted(time2fix, key=lambda x: (x[0] is None, x[0]))

hash2time = {}
hash2type = {}
for elem in sorted_time2fix:
    cur = time.mktime(elem[0])
    sec = cur - init_time
    if (elem[1] != None) and (elem[1] not in hash2time.keys()):
        hash2time[elem[1]] = sec
        if (elem[2] == True):
            hash2type[elem[1]] = 'crash'
        else:
            hash2type[elem[1]] = 'logic'

print(hash2time)
print(hash2type)
with open(os.path.join(bisect_dir, "result.txt"), 'w') as of:
    for e in list(hash2time.keys()):
        of.write(f'{e}, {hash2type[e]}, {hash2time[e]}\n')
