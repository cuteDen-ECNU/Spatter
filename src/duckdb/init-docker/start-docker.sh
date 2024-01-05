# docker pull postgis/postgis
docker_name=$1

mkdir -p "$(pwd)/${docker_name}/log"
chmod -R 777 "$(pwd)/${docker_name}/log"

docker rm -f ${docker_name}
docker build -t my-duckdb-image .
docker run --cap-add=SYS_PTRACE --tmpfs /run/lock --tmpfs /run \
  -v "$(pwd)/${docker_name}/log:/log" \
  --name ${docker_name} \
  -d my-duckdb-image

# docker run -it --rm -v $PWD:/host alpine
