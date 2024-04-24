docker_name=postgis-spatter
docker cp script $docker_name:/
docker exec -it $docker_name /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -f script/script/test.sql
