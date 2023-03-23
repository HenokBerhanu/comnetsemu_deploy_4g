LOG_ARGS="--log.all_level=debug"

PORT_ARGS="tx_port=tcp://*:2000,rx_port=tcp://10.80.97.3:2001"
ZMQ_ARGS="--rf.device_name=zmq --rf.device_args=\"${PORT_ARGS},id=enb,fail_on_disconnect=true,base_srate=23.04e6\""

OTHER_ARGS="--enb.mme_addr=10.80.95.10 --enb.gtp_bind_addr=10.80.95.11 --enb.s1c_bind_addr=10.80.95.11 --enb_files.sib_config=/etc/srsran/sib.conf"

sudo srsenb enb.conf ${LOG_ARGS} ${ZMQ_ARGS} ${OTHER_ARGS} $@