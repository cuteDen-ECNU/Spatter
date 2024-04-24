import datetime
import json
import os
import subprocess
from sys import argv
import time

from Spatter.InsertGenerator import InsertErrorBox
from Spatter.Log import Log
from Spatter.Executor import Executor

# postgis_new='4338f0b59'

# postgis_old='14464b4f5'

# commits_json = {}

# with open('/log/compile-geos.json') as of:
#     commits = json.load(of)
#     filtered_commits = {commit: data for commit, data in commits.items() if data["success"]}
#     sorted_commits = dict(sorted(filtered_commits.items(), key=lambda x: x[1]["time"]))
#     commits_json['geos'] = sorted_commits

# with open('/log/compile-postgis.json', 'r') as of:
#     commits = json.load(of)
#     filtered_commits = {commit: data for commit, data in commits.items() if data["success"]}
#     sorted_commits = dict(sorted(filtered_commits.items(), key=lambda x: x[1]["time"]))
#     commits_json['postgis'] = sorted_commits

commits = []
with open('/log/compile-hash') as of:
    lines = of.readlines()
    for line in lines:
        commits.append('-'.join(line[:-1].split(', ')))



log = Log()

executor = Executor(log)

insertErrorBox = InsertErrorBox()
insertErrorBox.UseAll()
queryError = ['GEOSOverlaps', 'GeoContains', 'TopologyException', 'This function only accepts LINESTRING as arguments.']        


def findCurNearestGeos(postgis_commits, geos_commits):
    for postgis_commit_id, postgis_commit_data in postgis_commits.items():
        postgis_time = datetime.datetime.strptime(postgis_commit_data["time"], "%Y-%m-%d-%H:%M:%S")
        
        closest_geos_commit_id = None
        closest_time_diff = None
        
        for geos_commit_id in reversed(geos_commits):
            geos_commit_data = geos_commits[geos_commit_id]
            geos_time = datetime.datetime.strptime(geos_commit_data["time"], "%Y-%m-%d-%H:%M:%S")
            
            if geos_time < postgis_time:
                closest_geos_commit_id = geos_commit_id
                closest_time_diff = postgis_time - geos_time
                break
        
        # print(f"For PostGIS commit {postgis_commit_id}, closest GEOS commit is {closest_geos_commit_id} with time difference {closest_time_diff}") 
        postgis_commits[postgis_commit_id]['geos'] = closest_geos_commit_id
    return postgis_commits



def install(postgis_commit):
    geos_commit = postgis_commit.split('-')[1]
    command1 = f'''cd /geos-commits/{geos_commit}/geos/build; make install;'''
    command2 = f'''cd /postgis-commits/{postgis_commit}/postgis; make install;'''
    executor.Execute('DROP extension postgis CASCADE;')
    
    try:
        subprocess.run(command1, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.WriteResult(command1, True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}\n{command1}")
        exit(-1)

    try:
        subprocess.run(command2, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.WriteResult(command2, True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}\n{command2}")
        exit(-1)

    executor.Execute('CREATE EXTENSION postgis;')
    executor.ExecuteSelect('SELECT postgis_full_version();')
        

def uninstall(postgis_commit):
    executor.Execute('DROP extension postgis CASCADE;')

    geos_commit = postgis_commit.split('-')[1]
    command1 = f'''cd /geos-commits/{geos_commit}/geos/build; make uninstall;'''
    command2 = f'''cd /postgis-commits/{postgis_commit}/postgis; make uninstall;'''
    
    try:
        subprocess.run(command1, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.WriteResult(command1, True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}\n{command1}")
        exit(-1)

    try:
        subprocess.run(command2, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.WriteResult(command2, True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}\n{command2}")
        exit(-1)
        

def check(d, i) -> bool:
    install(commits[i])

    t0_queries: str = d['t0_queries']
    query_list = t0_queries.replace(";", ";\n").split('\n')

    executor.ExecuteQueries(query_list, queryError + insertErrorBox.errors)

    if "crash" in d.keys():
        executor.ExecuteQueries([d["crash"]], queryError + insertErrorBox.errors)
        res = executor.error
        uninstall(commits[i])
        
        if(res == "crash"):
            return True
        else: 
            return False
    
    else:
        executor.ExecuteSelect(d["query1"], queryError + insertErrorBox.errors)
        res1 = executor.rows
        executor.ExecuteSelect(d["query2"], queryError + insertErrorBox.errors)
        res2 = executor.rows

        uninstall(commits[-1])
        
        if str(d["res1"]) != str(res1):
            return False
        if str(d["res2"]) != str(res2):
            return False
        return True

def reproduced(d: dict) -> bool:
    return check(d, len(commits) - 1)
    
def checkFixed(d: dict):
    return check(d, 0) != True

def binarySearchPostGIS(d):
    l = 0
    h = len(commits) - 1
    while(l < h):
        m = (l + h) // 2
        if check(d, m):
            h = m - 1
        else:
            l = m + 1
    return l


if __name__ == "__main__":

    folder_path = argv[1] # the path contianing trigger-cases
    all_entries = [entry for entry in os.listdir(folder_path) if not entry.endswith('.log')]
    
    if "example" in folder_path:
        file_names = all_entries
    else:
        name2times = []
        for entry in all_entries:
            if os.path.isfile(os.path.join(folder_path, entry)):
                t = time.strptime(entry[:19], "%Y-%m-%d-%H:%M:%S")
                name2time = [entry, t]
                name2times.append(name2time)
        name2times_sorted = sorted(name2times, key=lambda x: (x[1] is None, x[1]))
        file_names = [n[0] for n in name2times_sorted]

    of_result = open(f'{folder_path}-bisection.log', 'w')

    start = time.time()
    for file in file_names:
        if "result" in file or "error" in file:
            continue
        
        induce_path = os.path.join(folder_path, file)
        log.ChangeFilePath(induce_path)

        with open(induce_path, 'r') as of:
            d:dict = json.load(of)
        
        
        if (reproduced(d) == False):
            of_result.write(f"{file}: Not reproduced\n")
            continue


        fixed = checkFixed(d)

        if fixed == False:
            of_result.write(f"{file}: Not fixed\n")
            of_result.flush()
        else:
            l = binarySearchPostGIS(d)
            of_result.write(f"{file}: Is fixed at {commits[l]}\n")
        of_result.flush()
        # binary seach
    
 

    end = time.time()
            
    of_result.write(f"{len(file_names)} files costs {end - start}.")
