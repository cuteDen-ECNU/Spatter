


from datetime import datetime
import shutil
import subprocess
import psycopg2
from tqdm import tqdm


def read_commits():
    postgis_path = "/log/postgis-hash"
    geos_path = "/log/geos-hash"
    postgis_t2commit = []
    geos_t2commit = []
    
    with open(postgis_path,'r') as of:
        lines = of.readlines()
        for line in lines:
            commit, t = line.split()[0], datetime.strptime(line.split()[1], '%Y-%m-%d-%H:%M:%S')
            postgis_t2commit.append([commit, t])
    
    with open(geos_path,'r') as of:
        lines = of.readlines()
        for line in lines:
            commit, t = line.split()[0], datetime.strptime(line.split()[1], '%Y-%m-%d-%H:%M:%S')
            geos_t2commit.append([commit, t])    

    pn = len(postgis_t2commit); gn = len(geos_t2commit)
    
    pi = 0; gi = 0
    
    pcommit2gcommits = []

    while (pi < pn - 1) and (gi < gn):
        pcommit = postgis_t2commit[pi][0]
        ptime = postgis_t2commit[pi][1]
        gcommit = geos_t2commit[gi][0]
        gtime = geos_t2commit[gi][1]
        print(f'{pcommit}, {ptime}, {gcommit}, {gtime}, {(postgis_t2commit[pi + 1][1] <= geos_t2commit[gi][1]) or (gi == gn - 1) or (gi == 0)}')
        if (postgis_t2commit[pi + 1][1] <= geos_t2commit[gi][1]) or (gi == gn - 1) or (gi == 0):
            pcommit2gcommits.append([pcommit, gcommit, ptime, gtime])
            gi += 1
        else:
            pi += 1

    return pcommit2gcommits


def compile(pcommit2gcommits):
    print(len(pcommit2gcommits))
    # for line in tqdm(concurrent.futures.as_completed(futures), total=len(commits), desc="Compiling"):
    for line in tqdm(pcommit2gcommits):
        pcommit, gcommit, ptime, gtime = line[0], line[1], line[2], line[3]

        target_path = f"/postgis-commits/{pcommit}-{gcommit}/postgis"

        try:
            shutil.rmtree(target_path)
        except FileNotFoundError:
            pass
        
        shutil.copytree("/postgis", target_path)
        
        commands = f'''cd /geos-commits/{gcommit}/geos/build
make install
cd {target_path}
git config --global --add safe.directory {target_path}
git checkout {pcommit}
./autogen.sh
CFLAGS="-O0" CPPFLAGS="-O0" LDFLAGS=""
./configure --with-pgconfig=/usr/local/pgsql/bin/pg_config --with-geosconfig=/usr/local/bin/geos-config --without-protobuf --without-raster --without-topology --enable-debug 
make clean
make -j8
make install
'''
        tqdm.write(f"{pcommit}-{gcommit} install begin!")
        try:
            subprocess.run(commands, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open(f"/log/compile-postgis.log", 'a') as of:
                of.write(f"Processed command: {commands}\n")
            temp_record = {'success': True}  # Temporary record
        except subprocess.CalledProcessError as e:
            with open(f"/log/compile-postgis.log", 'a') as of:
                of.write(f"Error executing command for command {commands}: {e}")

        db_params = {'host': "localhost",
            'port': "5432", 'database': "nyc", 'user': "postgres"}
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute('CREATE extension if not exists postgis;')
        cursor.execute('SELECT postgis_full_version();')
        row = cursor.fetchone()[0]
        if ("upgrade" in row):
            print(f"upgrade in row: " + commands)
            exit(-1)
        if (pcommit not in row):
            print(f"{pcommit} not in row: " + commands)
            exit(-1)
        tqdm.write(f"{pcommit}-{gcommit} install success!")

        commands = f'''cd /geos-commits/{gcommit}/geos/build
make uninstall'''
        try:
            subprocess.run(commands, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with open(f"/log/compile-postgis.log", 'a') as of:
                of.write(f"Processed command: {commands}\n")
        except subprocess.CalledProcessError as e:
            with open(f"/log/compile-postgis.log", 'a') as of:
                of.write(f"Error executing command for command {commands}: {e}")



if __name__ == "__main__":
    pcommit2gcommits = read_commits()
    with open('/log/compile-hash', 'w') as of:
        for pg in pcommit2gcommits:
            of.write(f'{pg[0]}, {pg[1]}\n')
    compile(pcommit2gcommits)



