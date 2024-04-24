import json
import os
import shutil
import subprocess
import argparse
import concurrent.futures
from tqdm import tqdm

record = {}

def read_commits(path):
    with open(path) as of:
        lines = of.readlines()
        commits = []
        for i in range(len(lines)):  # Just for testing, change this to read all commits
            line = lines[i]
            commit = line.split()[0]
            commits.append(commit)
            record[commit] = {}
            record[commit]['time'] = line.split()[1]
    return commits

def compile(commit, module):
    repo_path = f"/{module}"

    commands = '''cd /{module}-commits/{commit}/{module}
git config --global --add safe.directory /{module}-commits/{commit}/{module}
git checkout {commit}'''
    
    if module == 'postgis':
        commands += '''
./autogen.sh
CFLAGS="-O0" CPPFLAGS="-O0" LDFLAGS=""
./configure --with-pgconfig=/usr/local/pgsql/bin/pg_config --with-geosconfig=/usr/local/bin/geos-config --without-protobuf --without-raster --without-topology --enable-debug 
make clean
make -j8
'''
    else:
        commands += '''
rm -r build
mkdir build
cd build
../configure
cmake .. 
make -j8
'''

    target_path = f"/{module}-commits/{commit}/{module}"
    
    try:
        shutil.rmtree(target_path)
    except FileNotFoundError:
        pass
    
    shutil.copytree(repo_path, target_path)
    
    try:
        subprocess.run(commands.format(commit=commit, module=module), shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(f"/log/compile-{module}.log", 'a') as of:
            of.write(f"Processed commit: {commit}\n")
        temp_record = {'success': True}  # Temporary record
    except subprocess.CalledProcessError as e:
        with open(f"/log/compile-{module}.log", 'a') as of:
            of.write(f"Error executing command for commit {commit}: {e}")
        temp_record = {'success': False}  # Temporary record
    
    return commit, temp_record  # Return commit and its record

def compile_parallel(commits, module, max_workers=None):
    target_path = f"/{module}-commits"
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for commit in commits:
            tqdm.write(f"{commit} begin...")
            future = executor.submit(compile, commit, module)
            futures[future] = commit

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(commits), desc="Compiling"):
            commit = futures[future]
            try:
                result = future.result()
                commit, temp_record = result
                record[commit].update(temp_record)  # Update main record with temporary record
            except Exception as e:
                print(f"Error compiling commit {commit}: {e}")

def collect_records(module):
    # Save the collected records as a JSON file
    with open(f"/log/compile-{module}.json", "w") as json_file:
        json.dump(record, json_file, indent=4)

if __name__ == "__main__":

    module = "geos"
    commits = read_commits(f"/log/{module}-hash")
    # 设置max_workers为None，让系统自动选择合适的核心数
    compile_parallel(commits, module, max_workers=8)
    
    collect_records(module)  # Call this function after all processes are done
