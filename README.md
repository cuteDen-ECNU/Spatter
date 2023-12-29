# Spatter


## Quick Start for PostGIS

Make sure the docker name and port, for example:
```
docker_name=postgis-spatter
docker_port=15450
```

Create docker:
```
docker_name=postgis-spatter
cd src/postgis
./init-docker/start-docker.sh ${docker_name} ${docker_port}
```

Compile the latest version of PostGIS:
```
docker_name=postgis-spatter
postgis_new='61bc019eb17eeade8640429e9de7c506621b4cb0'
geos_new='0aef713ac930e7247c50a1ae720c36f0f0bf790a'
docker exec ${docker_name} sh /src/compile/compile.sh ${postgis_new} ${geos_new}
```

Start postgres, create database, and create extension:
```
docker_name=postgis-spatter
./init-docker/start-psql.sh ${docker_name}
```

How to set parameter:
```
docker_name=postgis-spatter
docker exec -it ${docker_name} sh -c "./src/SpatterRun.py -h"
```

Run Spatter:
```
docker_name=postgis-spatter
docker exec -it ${docker_name} sh -c "./src/SpatterRun.py"
```

Reduce a single trigger case:
```
docker_name=postgis-spatter
trigger_path='/log/trigger-cases/2023-12-29-11:16:23-0'
docker exec -it ${docker_name} sh -c "./src/ReduceTest.py ${trigger_path}"
```

