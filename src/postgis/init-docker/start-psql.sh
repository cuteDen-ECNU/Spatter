docker_name=$1

docker exec -it -u postgres ${docker_name} sh -c "/usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data -l /usr/local/pgsql/data/logfile start"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -c "CREATE database nyc;"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -c "CREATE extension postgis;"
