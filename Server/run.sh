sudo chmod 644 /sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj

sudo docker build -t dummy_server .

docker run -d \
    --name dummy_server_1 \
    --cpus=5 \
    --memory=1g \
    -p 5001:5000 \
    dummy_server

docker run -d \
    --name dummy_server_2 \
    --cpus=5 \
    --memory=1g \
    -p 5002:5000 \
    dummy_server

docker run -d \
    --name dummy_server_3 \
    --cpus=5 \
    --memory=1g \
    -p 5003:5000 \
    dummy_server


