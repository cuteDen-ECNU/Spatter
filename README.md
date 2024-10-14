# Spatter

## Purpose
Spatter is a tool for finding Spatial related bugs in Spatial DBMS using Shape-Preserving Transformation.

## Supported Spatial DBMS
+ PostGIS
+ MySQL
+ DuckDB

## Effectiveness
+ [New bugs.](https://github.com/cuteDen-ECNU/bugs-record)

## Step by Step

### Quick Start for PostGIS

#### Install PostGIS
1. Make sure the docker name and port, for example:
```shell
docker_name=postgis-spatter
docker_port=15450
```

2. Create a docker
```shell
cd src/postgis
./init-docker/start-docker.sh ${docker_name} ${docker_port}
```

3. Install necessary dependancy
```shell
docker exec ${docker_name} sh -c "apt-get install -y bison flex cmake autoconf libtool libxml2-dev"
docker exec ${docker_name} sh -c "apt-get install -y libproj-dev libcunit1 libcunit1-doc libcunit1-dev lcov rsync"
docker exec ${docker_name} sh -c "pip install psycopg2-binary shapely "
```

4. Copy postgis source code from "src/postgis/script/src-repo"
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

5. Begin to compile
```shell
postgis_new='07a73c0f2'
geos_new='0a8fc37a9'
docker exec ${docker_name} sh /script/compile/compile.sh ${postgis_new} ${geos_new}
```

6. Start postgres, create database, and create extension
```shell
./init-docker/prepare-psql.sh ${docker_name}
./init-docker/start-psql.sh ${docker_name}
```

#### Run Spatter
7. How to set parameter:
```shell
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py -h"
```

8. Run Spatter:
```shell
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py"
```

9. Reduce a single trigger case:
```shell
trigger_path=/log/trigger-cases/$(docker exec -it ${docker_name} sh -c "ls /log/trigger-cases/ | head -n 1")
docker exec -it ${docker_name} sh -c "./script/SpatterReduce.py ${trigger_path}"
```

### Quick Start for DuckDB Spatial
#### Install DuckDB Spatial
1. Make sure the docker name, for example:
```shell
docker_name=duckdb-spatter
```
2. Create docker:
```shell
cd src/duckdb
./init-docker/start-docker.sh ${docker_name}
```
3. Compile duckdb:
```shell
docker exec ${docker_name} sh /script/compile/compile.sh
```

#### Run Spatter
4. Run Spatter:
```shell
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py"
```

5. Reduce a single trigger case:
```shell
trigger_path=$(docker exec -it ${docker_name} sh -c 'echo /log/trigger-cases/* | cut -d" " -f1')
docker exec -it ${docker_name} sh -c "./script/SpatterReduce.py ${trigger_path}"
```

### Quick Start for MySQL GIS
#### Install MySQL
1. Make sure the docker name, for example:
```shell
docker_name=mysql-spatter
docker_port=15451
```
2. Create docker:
```shell
cd src/mysql
./init-docker/start-docker.sh ${docker_name} ${docker_port}
```
3. Compile duckdb:
```shell
docker exec ${docker_name} sh /script/compile/compile.sh
```
#### Run Spatter
4. Start postgres, and create database:
```shell
./init-docker/start-mysql.sh ${docker_name}
```
5. Run Spatter:
```shell
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py"
```
6. Reduce a Single Trigger Case:
```shell
trigger_path=$(docker exec -it ${docker_name} sh -c 'echo /log/trigger-cases/* | cut -d" " -f1')
docker exec -it ${docker_name} sh -c "./script/SpatterReduce.py ${trigger_path}"
```


## Efficiency
+ [Run time distribution.](evaluation/proportion/README.md) Result and reproducing steps.
+ [Self-constructed baseline.](evaluation/unique-bugs/README.md) Result and reproducing steps.
