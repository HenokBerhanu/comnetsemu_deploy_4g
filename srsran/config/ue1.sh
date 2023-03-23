LOG_PARAMS="--log.all_level=info"

PORT_ARGS="tx_port=tcp://*:2001,rx_port=tcp://{IPS['enb']}:2000"
ZMQ_ARGS="--rf.device_name=zmq --rf.device_args=\"${PORT_ARGS},id=ue,fail_on_disconnect=true,base_srate=23.04e6\"

sudo srsue ue.conf ${LOG_PARAMS} ${ZMQ_ARGS} $@