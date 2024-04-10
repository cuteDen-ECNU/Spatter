

import json
import os
from matplotlib import pyplot as plt
import numpy as np



def collect_data(folder_path, N):
    files = os.listdir(folder_path)
    res_list = []
    
    for f in files:
        if "result" in f:
            with open(os.path.join(folder_path, f), 'r') as of:
                lines = of.readlines()
                config = json.loads(lines[0][2:].strip())
                geometry_number = config["geometry_number"]
                spatter_time = float(lines[-1][2:].strip())
                dbms_time = float(lines[-2][2:].strip())
                res_list.append([geometry_number, spatter_time, dbms_time])
    
    res_array = np.array(res_list)
    spatter_ave = np.mean(res_array[res_array[:, 0] == N, 1])
    spatter_std = np.std(res_array[res_array[:, 0] == N, 1])
    dbms_ave = np.mean(res_array[res_array[:, 0] == N, 2])
    dbms_std = np.std(res_array[res_array[:, 0] == N, 2])
    
    return spatter_ave, spatter_std, dbms_ave, dbms_std

N = ['1', '10', '50', '100']
titlesize = 20
legendsize = 16
plt.figure(figsize=(15,5)) 

of = open("evaluation/proportion/res.txt", "w")

def plot(dbms, file_path):

    spatter_times = []
    dbms_times = []
    for n in N:
        spatter_ave, spatter_std, dbms_ave, dbms_std = collect_data(file_path, int(n))
        spatter_times.append(spatter_ave - dbms_ave)
        dbms_times.append(dbms_ave)
        of.write(f'''{dbms}, {n}  \n''')
        of.write(f'''spatter: {spatter_ave} &plusmn; {spatter_std}  \n''')
        of.write(f'''dbms: {dbms_ave} &plusmn; {dbms_std}  \n''')

    plt.bar(N, dbms_times, label='SDBMS', color='#1289A7')
    plt.bar(N, spatter_times, label='Spatter', bottom=dbms_times, color='#A3CB38')  

    plt.title(dbms, fontsize=titlesize)
    plt.xlabel('N', fontsize=titlesize)
    plt.ylabel('Time (ms)', fontsize=titlesize)

    plt.tick_params(axis='x', labelsize=legendsize)  
    plt.tick_params(axis='y', labelsize=legendsize) 

    plt.legend(fontsize=legendsize)

plt.subplot(131)
plot("PostGIS", "src/postgis/postgis-spatter-15450/log/spatter")

plt.subplot(132)
plot("MySQL GIS", "src/mysql/mysql-spatter-15451/log/spatter")

plt.subplot(133)
plot("DuckDB Spatial", "src/duckdb/duckdb-spatter/log/spatter")


plt.tight_layout()
plt.savefig('doc/proportion/efficiency_study.pdf')


