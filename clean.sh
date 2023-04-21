#!/bin/bash

sudo mn -c

docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

docker container prune -f

if [ "$1" == "log" ]; then
    cd log && sudo rm *.log 
fi

sudo ip link del dev s1-gre1
sudo ip link del dev s2-gre1
sudo ip link del dev s3-gre1
sudo ip link delete s1-s2
sudo ip link delete s2-s3
sudo ip link delete s1-srseue
sudo ip link delete s2-srsenb
sudo ip link delete s3-epc
