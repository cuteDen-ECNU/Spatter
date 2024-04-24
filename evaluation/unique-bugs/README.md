# Unique bugs

## Results
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

# generation-based generator:
postgis-38d9c69f1dd5c0061d254d190aeb38795edea9d4, logic, 2.0
postgis-c1dbf8ef0007f8230b1ec76e4b3f9d079647dcb2, logic, 15.0
geos-bb1a02679949868419baf73c6c11ee6179a21627, crash, 547.0
```

PostGIS coverage (i.e., Figure 7(b))
```
# geometry-aware generator:
doc/unique-bugs/smart-gen-2024-01-08-07/coverage/postgis-2024-01-08-07:50:18.txt
# generation-based generator:
doc/unique-bugs/rand-gen-2024-01-10-03/coverage/postgis-2024-01-10-03:59:36.txt
```

GEOS coverage (i.e., Figure 7(c))
```
# geometry-aware generator:
doc/unique-bugs/smart-gen-2024-01-08-07/coverage/geos-2024-01-08-07:50:18.txt
# generation-based generator:
doc/unique-bugs/rand-gen-2024-01-10-03/coverage/geos-2024-01-10-03:59:36.txt
```

## Coverage

Configure:
```shell
cd <Spatter-root>/src/postgis
docker_name=postgis-spatter
docker_port=15450
```

Compile PostGIS with gcov:
```shell
# Choose the target version of PostGIS:
postgis_old='89fb963850b2492fe1e9d7eed1ca81b86f23e6da'
geos_old='0dc1901601fd226036e1b898a7ae026f2067a71a'
docker exec ${docker_name} sh /script/compile/compile_with_gcov.sh ${postgis_old} ${geos_old}
./init-docker/prepare-psql.sh ${docker_name}
./init-docker/start-psql.sh ${docker_name}

docker exec ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -c "CREATE USER root WITH SUPERUSER PASSWORD 'your_password'"
docker exec ${docker_name} sh /script/compile/check_gcov.sh
```

Then we can collect coverage info and induce cases.
For Geometry-Aware Generator:
```shell
docker exec -it ${docker_name} sh -c "python3 ./script/CoverageTest.py"
# terminate Spatter
docker exec $docker_name sh -c 'script/script/kill-python.sh'
docker cp $docker_name:/log ../../doc/unique-bugs/geometry-aware-gen
```

For Random-Shape Strategy:
```shell
docker exec -it ${docker_name} sh -c "python3 ./script/CoverageTest.py --smart_generator_on=0"
# terminate Spatter
docker exec $docker_name sh -c 'script/script/kill-python.sh'
docker cp $docker_name:/log ../../doc/unique-bugs/random-shape-gen
```

## Binary search for unique bugs 

### 1. Compile commits of PostGIS and GEOS 
```shell
docker_name=postgis-spatter
docker cp script ${docker_name}:/
docker exec -it ${docker_name} sh -c "cd /postgis; git log --format='%h %cd' --date=format:'%Y-%m-%d-%H:%M:%S' --since='2023-10-20' > /log/postgis-hash"

docker exec -it ${docker_name} sh -c "cd /geos; git log --format='%h %cd' --date=format:'%Y-%m-%d-%H:%M:%S' --since='2023-10-20' > /log/geos-hash"

docker exec -it ${docker_name} sh -c "pip install tqdm"
docker exec -it ${docker_name} sh -c "python3 script/compile/geos-compile-commits.py"
docker exec -it ${docker_name} sh -c "python3 script/compile/postgis-compile-commits.py"
```

### 2. Check Compiling Results by Reproduction

```shell
docker_name=postgis-spatter
# docker exec -it ${docker_name} sh -c "rm -r /log/example/*.log"
docker exec -it ${docker_name} sh -c "python3 /script/binary-search.py /log/example"
docker exec -it ${docker_name} sh -c "cat /log/example-bisection.log"
```
If all the test cases are fixed, the [Step 1](#1-compile-commits-of-postgis-and-geos) successed. 

### 3. Binary Search for Trigger Cases

```shell
# docker exec -it ${docker_name} sh -c "rm -r /log/trigger-case/*.log"
docker exec -it ${docker_name} sh -c "python3 /script/binary-search.py /log/trigger-case"

```


