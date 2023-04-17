#!/bin/bash

LOG_ARGS="--log.all_level=debug --log.all_level=info --log.filename=/tmp/srsran_logs/enb.log"

PORT_ARGS="tx_port=tcp://*:2101,rx_port=tcp://localhost:2100"
ZMQ_ARGS="--rf.device_name=zmq --rf.device_args=\'${PORT_ARGS},id=enb,base_srate=23.04e6\'"

#OTHER_ARGS="--enb_files.sib_config=/etc/srsran/sib.conf --enb_files.rr_config=/etc/srsran/rr.conf --enb_files.rb_config=/etc/srsran/rb.conf"
OTHER_ARGS="--enb_files.sib_config=/etc/srsran/sib.conf"

exec.run = "/etc/srsran/enb.conf ${LOG_ARGS} ${ZMQ_ARGS} ${OTHER_ARGS} $@"