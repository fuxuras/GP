docker stop dummy_server_1
docker stop dummy_server_2
docker stop dummy_server_3

docker container remove dummy_server_1
docker container remove dummy_server_2
docker container remove dummy_server_3


sudo chmod 644 /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj

sudo docker build -t dummy_server .

docker run -d \
    --name dummy_server_1 \
    --cpus=5 \
    --memory=1g \
    -p 8001:8000 \
    dummy_server

docker run -d \
    --name dummy_server_2 \
    --cpus=5 \
    --memory=1g \
    -p 8002:8000 \
    dummy_server

docker run -d \
    --name dummy_server_3 \
    --cpus=5 \
    --memory=1g \
    -p 8003:8000 \
    dummy_server


