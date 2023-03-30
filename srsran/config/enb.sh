LOG_ARGS="--log.all_level=debug"

PORT_ARGS="tx_port=tcp://*:2000,rx_port=tcp://10.80.97.12:2001"
ZMQ_ARGS="--rf.device_name=zmq --rf.device_args=\"${PORT_ARGS},id=enb,fail_on_disconnect=true,base_srate=23.04e6\""

OTHER_ARGS="--enb_files.rr_config=rr.conf"

sudo srsenb enb.conf ${LOG_ARGS} ${ZMQ_ARGS} ${OTHER_ARGS} $@