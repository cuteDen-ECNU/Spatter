# Spatter

## Purpose
Spatter is a tool for finding Spatial related bugs in Spatial DBMS using Shape-Preserving Transformation.

## Supported Spatial DBMS
+ PostGIS
+ MySQL
+ DuckDB

## Step by Step

### Quick Start for PostGIS
```
# Make sure the docker name and port, for example:
docker_name=postgis-spatter
docker_port=15450

# Create docker:
cd src/postgis
./init-docker/start-docker.sh ${docker_name} ${docker_port}

# Choose the target version of PostGIS:
postgis_new='61bc019eb17eeade8640429e9de7c506621b4cb0'
geos_new='0aef713ac930e7247c50a1ae720c36f0f0bf790a'
docker exec ${docker_name} sh /script/compile/compile.sh ${postgis_new} ${geos_new}

# Start postgres, create database, and create extension:
./init-docker/start-psql.sh ${docker_name}

# How to set parameter:
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py -h"

# Run Spatter:
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py"

# Reduce a single trigger case:
trigger_path=/log/trigger-cases/$(docker exec -it ${docker_name} sh -c "ls /log/trigger-cases/ | head -n 1")
docker exec -it ${docker_name} sh -c "./script/SpatterReduce.py ${trigger_path}"
```

### Quick Start for DuckDB Spatial
```
# Make sure the docker name, for example:
docker_name=duckdb-spatter

# Create docker:
cd src/duckdb
./init-docker/start-docker.sh ${docker_name}

# Compile duckdb:
docker exec ${docker_name} sh /script/compile/compile.sh

# Run Spatter:
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py"

# Reduce a single trigger case:
trigger_path=$(docker exec -it ${docker_name} sh -c 'echo /log/trigger-cases/* | cut -d" " -f1')
docker exec -it ${docker_name} sh -c "./script/SpatterReduce.py ${trigger_path}"
```

### Quick Start for MySQL GIS
```
# Make sure the docker name, for example:
docker_name=mysql-spatter
docker_port=15451

# Create docker:
cd src/mysql
./init-docker/start-docker.sh ${docker_name} ${docker_port}

# Compile duckdb:
docker exec ${docker_name} sh /script/compile/compile.sh

# Start postgres, and create database:
./init-docker/start-mysql.sh ${docker_name}

# Run Spatter:
docker exec -it ${docker_name} sh -c "./script/SpatterRun.py"

# Reduce a single trigger case:
trigger_path=$(docker exec -it ${docker_name} sh -c 'echo /log/trigger-cases/* | cut -d" " -f1')
docker exec -it ${docker_name} sh -c "./script/SpatterReduce.py ${trigger_path}"
```