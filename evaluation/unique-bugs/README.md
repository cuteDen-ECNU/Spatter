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
```shell
docker exec -it ${docker_name} sh -c "python3 ./script/CoverageTest.py"
# terminate Spatter
docker exec $docker_name sh -c 'script/script/kill-python.sh'
```


## Binary search for unique bugs 

### 1. Compile commits of PostGIS and GEOS 
```shell
docker cp script ${docker_name}:/
docker exec -it ${docker_name} sh -c "cd /postgis; git log --format='%h %cd' --date=format:'%Y-%m-%d-%H:%M:%S' --invert-grep --grep='Translated' ${postgis_old}^..HEAD > /log/postgis-hash"

docker exec -it ${docker_name} sh -c "cd /geos; git log --format='%h %cd' --date=format:'%Y-%m-%d-%H:%M:%S'  ${geos_old}^..HEAD > /log/geos-hash"

docker exec -it ${docker_name} sh -c "pip install tqdm"
docker exec -it ${docker_name} sh -c "python3 script/compile/compile-commits.py --module postgis"
docker exec -it ${docker_name} sh -c "python3 script/compile/compile-commits.py --module geos"
```

### 2. Check compiling results of PostGIS
```shell
EXPECTED_VERSION=c1dbf8ef0
docker exec -it ${docker_name} sh -c "cd postgis-commits/$EXPECTED_VERSION/postgis;make install"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -c "DROP extension postgis CASCADE; CREATE extension postgis; SELECT postgis_full_version() LIKE '%$EXPECTED_VERSION%' AS check_result;"
```
If you encounter issues, please refer to [Step 1](#1-compile-commits-of-postgis-and-geos) for compiling PostGIS and GEOS commits.


### 3. Check compiling results of GEOS
Check whether crash reproduced:
```shell
REPRO_VERSION=34b29f889
docker exec -it ${docker_name} sh -c "cd geos-commits/$REPRO_VERSION/geos/build;make install"
docker exec -it ${docker_name} sh -c "/usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -f /script/script/check-geos.sql"
```
Check whether crash fixed:
```shell
FIX_VERSION=bb1a02679
docker exec -it ${docker_name} sh -c "cd geos-commits/$FIX_VERSION/geos/build;make install"
docker exec -it ${docker_name} sh -c "/usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -f /script/script/check-geos.sql"
```



# Save data
```
docker cp $docker_name:/log ../../doc/unique-bugs/2024-01-08-07
```

<!-- 
Compile DuckDB Spatial with gcov:
```
cd <Spatter-root>/src/duckdb
docker_name=duckdb-spatter

# compile with gcov and check whether it is successful
docker exec ${docker_name} sh /script/compile/compile_with_gcov.sh
docker exec ${docker_name} sh /script/compile/check_gcov.sh
```

Then we collect the coverage info:
```
docker exec -it ${docker_name} sh -c "python3 ./script/CoverageTest.py"
``` -->


docker exec -it ${docker_name} sh -c "rm -r postgis-commits"
docker exec -it ${docker_name} sh -c "ls -l postgis-commits"
docker exec -it ${docker_name} sh -c "ps -elf |grep python"
docker restart ${docker_name}

docker exec -it ${docker_name} sh -c "cd geos; git pull origin main"

docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -c "DROP extension postgis CASCADE;"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -c "CREATE extension postgis;"


docker exec -it ${docker_name} sh -c "python3 /script/binary-search.py /log/json_induce_case_example"

docker exec -it ${docker_name} sh -c "rm /log/json_induce_case_example/*.log"
docker exec -it ${docker_name} sh -c "/usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -f /script/script/test.sql"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -c "SELECT postgis_extensions_upgrade();"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -f /postgis-commits/86db77037/postgis/extensions/postgis/sql/postgis_upgrade.sql"

docker exec -it ${docker_name} sh -c "find . -name postgis_upgrade.sql"
