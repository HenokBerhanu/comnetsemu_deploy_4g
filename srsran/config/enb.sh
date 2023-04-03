LOG_ARGS="--log.all_level=info", "--log.filename=/tmp/srsran_logs/enb.log"

ZMQ_ARGS="--rf.device_name=zmq --rf.device_args='id=enb,fail_on_disconnect=true,tx_port=tcp://*:2001,rx_port=tcp://192.168.56.101:3000,base_srate=23.04e6'"

OTHER_ARGS="--enb_files.sib_config=sib.conf"

docker exec srsenb enb.conf ${LOG_ARGS} ${ZMQ_ARGS} ${OTHER_ARGS} $@