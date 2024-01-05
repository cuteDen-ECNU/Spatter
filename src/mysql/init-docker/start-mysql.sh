docker_name=$1

docker exec -it ${docker_name} sh -c "script/compile/compile.sh"

docker exec -it ${docker_name} sh -c "useradd -r -m -s /bin/false mysqluser"
docker exec -it ${docker_name} sh -c "chown -R mysqluser:mysqluser /usr/local/mysql"
docker exec -it -u mysqluser ${docker_name} sh -c "/usr/local/mysql/bin/mysqld --initialize-insecure --datadir=/usr/local/mysql/data"

docker exec -it -u mysqluser ${docker_name} sh -c "/usr/local/mysql/bin/mysqld --datadir=/usr/local/mysql/data --port=3306 --daemonize"

docker exec -it -u mysqluser ${docker_name} sh -c "/usr/local/mysql/bin/mysql -u root -e 'CREATE DATABASE nyc;'"


