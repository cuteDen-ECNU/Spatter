# Results
Unique bugs (i.e., Figure 7(a))

```
# geometry-aware generator:
postgis-38d9c69f1dd5c0061d254d190aeb38795edea9d4, logic, 1.0
postgis-c1dbf8ef0007f8230b1ec76e4b3f9d079647dcb2, logic, 87.0
geos-bb1a02679949868419baf73c6c11ee6179a21627, crash, 95.0
postgis-bf6be27c3ca640c21abfee118863d9bdb58bb02f, logic, 246.0
geos-7d8455ce42677411c3d4ee950928506eb65745e1, crash, 507.0
geos-136e8e486f13e590da6096c196c49bc6ca272b2c, logic, 619.0
postgis-89b31d970de2975320c4a4b76c9dd5a0760b51d8, crash, 1532.0

# random-shape generator:
postgis-38d9c69f1dd5c0061d254d190aeb38795edea9d4, logic, 2.0
postgis-c1dbf8ef0007f8230b1ec76e4b3f9d079647dcb2, logic, 15.0
geos-bb1a02679949868419baf73c6c11ee6179a21627, crash, 547.0
```

PostGIS coverage (i.e., Figure 7(b))
+ [geometry-aware generator](../../doc/unique-bugs/smart-gen-2024-01-08-07/coverage/postgis-2024-01-08-07:50:18.txt)
+ [random-shape generator](../../doc/unique-bugs/rand-gen-2024-01-10-03/coverage/postgis-2024-01-10-03:59:36.txt)

GEOS coverage (i.e., Figure 7(c))
+ [geometry-aware generator](../../doc/unique-bugs/smart-gen-2024-01-08-07/coverage/geos-2024-01-08-07:50:18.txt)
+ [random-shape generator](../../doc/unique-bugs/rand-gen-2024-01-10-03/coverage/geos-2024-01-10-03:59:36.txt)

# Reproduce

There are two step to reproduce the results:
+ First we need to collect bug-inducing cases and coveragte information generated during a 1-hour run.
+ Second, we search for the fix of each bug-inducing cases. 

We use two dockers to reproduce the results.

## Collect Coverage Information and Bug-Inducing Cases
1. Configure:
```shell
cd <Spatter-root>/src/postgis
docker_name=postgis-spatter-coverage
docker_port=15451
```

Create a docker:
```shell
cd <Spatter-root>/src/postgis
./init-docker/start-docker.sh ${docker_name} ${docker_port}
```

2. Compile PostGIS with gcov:
Copy postgis source code from "src/postgis/script/src-repo"
```shell
docker exec ${docker_name} sh -c "mv /script/src-repo/postgres-main /postgres"
docker exec ${docker_name} sh -c "mv /script/src-repo/geos-main /geos"
docker exec ${docker_name} sh -c "mv /script/src-repo/postgis-main /postgis"
```

Or choose the newest version of PostGIS through github:
```shell
docker exec ${docker_name} sh -c "git clone https://github.com/postgres/postgres.git || exit -1"
docker exec ${docker_name} sh -c "git clone https://github.com/libgeos/geos.git || exit -1"
docker exec ${docker_name} sh -c "git clone https://github.com/postgis/postgis.git || exit -1"
```
Begin to compile:
```shell
postgis_old='89fb96385'
geos_old='0dc190160'
docker exec ${docker_name} sh /script/compile/compile_with_gcov.sh ${postgis_old} ${geos_old}

# Start postgres, create database, and create extension:
./init-docker/prepare-psql.sh ${docker_name}
./init-docker/start-psql.sh ${docker_name}

# create root user
docker exec ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -c "CREATE USER root WITH SUPERUSER PASSWORD 'your_password'"

# check
docker exec ${docker_name} sh /script/compile/check_gcov.sh
```

Then we can collect coverage info and induce cases.
### Geometry-Aware Generator
```shell
docker exec -it ${docker_name} sh -c "python3 ./script/CoverageTest.py"
```

Terminate Spatter and Save Data
```shell
docker exec $docker_name sh -c 'script/script/kill-python.sh'
docker cp $docker_name:/log ../../doc/unique-bugs/geometry-aware-gen
```

### Random-Shape Strategy
```shell
docker exec -it ${docker_name} sh -c "python3 ./script/CoverageTest.py --smart_generator_on=0"
```

Terminate Spatter and Save Data
```shell
docker exec $docker_name sh -c 'script/script/kill-python.sh'
docker cp $docker_name:/log ../../doc/unique-bugs/random-shape-gen
```

## Binary Search for Unique Bugs

### Compile Commits of PostGIS and GEOS (Time Consuming)

1. Creating a new docker to avoid gcov residue <a id="restart"></a>

Configure:
```shell
docker_name=postgis-spatter-bisection
docker_port=15452
```
Create a docker:
```shell
cd <Spatter-root>/src/postgis
./init-docker/start-docker.sh ${docker_name} ${docker_port}
```

2. Compile the newest version of Postgis

Copy postgis source code from "src/postgis/script/src-repo"
```shell
docker exec ${docker_name} sh -c "mv /script/src-repo/postgres-main /postgres"
docker exec ${docker_name} sh -c "mv /script/src-repo/geos-main /geos"
docker exec ${docker_name} sh -c "mv /script/src-repo/postgis-main /postgis"
```

Or choose the newest version of PostGIS through github:
```shell
docker exec ${docker_name} sh -c "git clone https://github.com/postgres/postgres.git || exit -1"
docker exec ${docker_name} sh -c "git clone https://github.com/libgeos/geos.git || exit -1"
docker exec ${docker_name} sh -c "git clone https://github.com/postgis/postgis.git || exit -1"
```
Begin to compile:
```shell
postgis_new='07a73c0f2'
geos_new='0a8fc37a9'
docker exec ${docker_name} sh /script/compile/compile.sh ${postgis_new} ${geos_new}

# Start postgres, create database, and create extension:
./init-docker/prepare-psql.sh ${docker_name}
./init-docker/start-psql.sh ${docker_name}
```

3. Collect version information during our test campaign.
(since '2023-10-20', before '2024-03-01')
```shell
docker_name=postgis-spatter
docker cp script ${docker_name}:/
docker exec -it ${docker_name} sh -c "cd /postgis; git log --format='%h %cd' --date=format:'%Y-%m-%d-%H:%M:%S' --since='2023-10-20' --before='2024-03-01' > /log/postgis-hash"

docker exec -it ${docker_name} sh -c "cd /geos; git log --format='%h %cd' --date=format:'%Y-%m-%d-%H:%M:%S' --since='2023-10-20' --before='2024-03-01' > /log/geos-hash"
```
4. Compile PostGIS and GEOS of versions during our test campaign.
```shell
docker exec -it ${docker_name} sh -c "pip install tqdm"
docker exec -it ${docker_name} sh -c "python3 script/compile/geos-compile-commits.py"
docker exec -it ${docker_name} sh -c "python3 script/compile/postgis-compile-commits.py"
```

If Step 2 run incorrectly, back to [Step 1](#restart).

### 2. Check Compiling Results by Reproduction

```shell
docker_name=postgis-spatter
# docker exec -it ${docker_name} sh -c "rm -r /log/example/*.log"
docker exec -it ${docker_name} sh -c "python3 /script/binary-search.py /log/example"
```
Check whether the test cases are fixed.
```shell
docker exec -it ${docker_name} sh -c "cat /log/example-bisection.log"
```
If all the test cases are fixed, the compiling process successed. 
Otherwise, back to [Step 1](#restart).

### 3. Binary Search for Trigger Cases

Copy the trigger cases.
Note that we need to change <strategy-name> to "random-shape-gen" or "geometry-aware-gen".
```shell
docker cp ../../doc/unique-bugs/<strategy-name>/trigger-cases/ ${docker_name}:/log/trigger-case
```

Binary search each trigger case for the fix.
```shell
docker exec -it ${docker_name} sh -c "python3 /script/binary-search.py /log/trigger-case"
```
Check the results.
```shell
docker exec -it ${docker_name} sh -c "cat /log/trigger-case-bisection.log"
```

