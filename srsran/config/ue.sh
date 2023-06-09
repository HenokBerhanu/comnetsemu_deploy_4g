#!/bin/bash

./config/srsran/enb.confd &


sleep 5
./config/srsran/sib.confd &
./config/srsran/rr.confd &
./config/srsran/rb.confd &
./config/srsran/ue.confd &

# LOG_PARAMS="--log.all_level=info", "--log.filename=/tmp/srsran_logs/ue.log"

# ZMQ_ARGS="--rf.device_name=zmq --rf.device_args='id=ue,fail_on_disconnect=true,tx_port=tcp://*:2001,rx_port=tcp://localhost:2000,base_srate=23.04e6' --gw.netns=ue1"

## Create netns for UE
ip netns list | grep "ue1" > /dev/null
if [ $? -eq 1 ]; then
  echo creating netspace ue1...
  sudo ip netns add ue1
  if [ $? -ne 0 ]; then
   echo failed to create netns ue1
   exit 1
  fi
fi

#exec srsue ue.conf ${LOG_PARAMS} ${ZMQ_ARGS} --rat.eutra.dl_earfcn=3350 "$@"