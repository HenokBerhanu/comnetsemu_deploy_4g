#!/bin/bash

./config/srsran/enb.confd &


sleep 5
./config/srsran/sib.confd &
./config/srsran/rr.confd &
./config/srsran/rb.confd &

# LOG_ARGS="--log.all_level=info", "--log.filename=/tmp/srsran_logs/enb.log"

# ZMQ_ARGS="--rf.device_name=zmq --rf.device_args='id=enb,fail_on_disconnect=true,tx_port=tcp://*:2000,rx_port=tcp://0.0.0.0:2001,base_srate=23.04e6'"

# OTHER_ARGS="--enb_files.sib_config=sib.conf"

# exec srsenb enb.conf ${LOG_ARGS} ${ZMQ_ARGS} ${OTHER_ARGS} $@