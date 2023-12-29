# docker pull postgis/postgis
docker_name=$1
docker_port=$2

mkdir -p "$(pwd)/${docker_name}-${docker_port}/log"
chmod -R 777 "$(pwd)/${docker_name}-${docker_port}/log"
cp config/coverage.conf $(pwd)/${docker_name}-${docker_port}/log/

docker rm -f ${docker_name}
docker build -t my-postgis-image .
docker run --tmpfs /run/lock --tmpfs /run \
  --cap-add=SYS_PTRACE \
  -v "$(pwd)/${docker_name}-${docker_port}/log:/log" \
 -p ${docker_port}:5432 --name ${docker_name} \
 -e POSTGRES_PASSWORD=mysecretpassword -d my-postgis-image


# docker run -it --rm -v $PWD:/host alpine
