#!/bin/bash

sudo mn -c

docker stop $(docker ps -aq)

docker container prune -f