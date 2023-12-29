docker_name=$1

docker exec -it ${docker_name} sh -c "rm -r /usr/local/pgsql/data"

docker exec -it ${docker_name} sh -c "chmod +x /usr/local/lib/libgeos_c.so.1.*"

docker exec -it ${docker_name} sh -c "useradd postgres"
docker exec -it ${docker_name} sh -c "chown -R postgres:postgres /usr/local/pgsql"
docker exec -it ${docker_name} sh -c "chown -R root:postgres /postgis"
docker exec -it ${docker_name} sh -c "chmod -R ug+w /postgis"
docker exec -it ${docker_name} sh -c "chown -R root:postgres /geos"
docker exec -it ${docker_name} sh -c "chmod -R ug+w /geos"

docker exec -it -u postgres ${docker_name} sh -c "rm -r /usr/local/pgsql/data"
docker exec -it -u postgres ${docker_name} /usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data

docker exec -it -u postgres ${docker_name} sh -c "echo 'host all postgres 172.17.0.1/32 trust' >> /usr/local/pgsql/data/pg_hba.conf"
docker exec -it -u postgres ${docker_name} sh -c "sed -i 's/^#listen_addresses = .*/listen_addresses = '\''*'\''/' /usr/local/pgsql/data/postgresql.conf"

docker exec -it -u postgres ${docker_name} sh -c "export LD_PRELOAD=/usr/lib/gcc/x86_64-linux-gnu/11/libasan.so:$LD_PRELOAD"
docker exec -it -u postgres ${docker_name} sh -c "/usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data -l /usr/local/pgsql/data/logfile start"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -c "CREATE database nyc;"
docker exec -it ${docker_name} /usr/local/pgsql/bin/psql -U postgres -h localhost -p 5432 -d nyc -c "CREATE extension postgis;"
