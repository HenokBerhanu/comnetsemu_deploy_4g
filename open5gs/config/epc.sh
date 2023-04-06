#!/bin/bash

export DB_URI="mongodb://localhost/open5gs"

mongod --smallfiles --dbpath /var/lib/mongodb --logpath /open5gs/install/var/log/open5gs/mongodb.log --logRotate reopen --logappend --bind_ip_all &


sleep 10 && cd webui && npm run dev &


./install/bin/open5gs-hssd &
./install/bin/open5gs-pcrfd &

sleep 5
./install/bin/open5gs-smfd &
./install/bin/open5gs-mmed &
./install/bin/open5gs-sgwcd &

sleep 15
./install/bin/open5gs-sgwud &
./install/bin/open5gs-upfd