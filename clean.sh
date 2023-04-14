#!/bin/bash

sudo mn -c

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

docker container prune -f

if [ "$1" == "log" ]; then
    cd log && sudo rm *.log 
fi

sudo ip link delete s1-s2
sudo ip link delete s2-s3
sudo ip link delete s1-ue
sudo ip link delete s2-enb
sudo ip link delete s3-epc