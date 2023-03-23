#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import atexit
import os
import shlex
import signal
import subprocess
import time
from typing import Dict, List
#import os

from comnetsemu.cli import CLI, spawnXtermDocker
from comnetsemu.net import Containernet, VNFManager
from mininet.link import TCLink, TCIntf
from mininet.log import info, setLogLevel
from mininet.node import Controller, OVSBridge
from mininet.topo import Topo

if __name__ == "__main__":

    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")

    prj_folder="/home/vagrant/comnetsemu_deploy_4g"
    mongodb_folder="/home/vagrant/mongodbdata"

    env = dict()
    IPS: Dict[str, str] = {
    #"epc": "10.80.95.10",
    "enb": "10.80.95.11",
    "ue": "10.80.97.12",
} 
    
    net = Containernet(controller=Controller, ipBase="10.0.0.0/8", link=TCLink, waitConnected=True)

    cmds: Dict[DockerHost, str] = {}
    hardcoded_ips: List[Dict[str, str]] = []

    info("*** Adding Host for open5gs EPC\n")
    epc = net.addDockerHost(
        "epc",
        dimage="o5gs_epc",
        ip="10.80.95.0/24",
        # dcmd="",
        dcmd="bash /open5gs/install/etc/open5gs/epc.sh",
        docker_args={
            "ports" : { "3000/tcp": 3000 },
            "volumes": {
                prj_folder + "/epclog": {
                    "bind": "/open5gs/install/var/log/open5gs",
                    "mode": "rw",
                },
                mongodb_folder: {
                    "bind": "/var/lib/mongodb",
                    "mode": "rw",
                },
                prj_folder + "/open5gs/config": {
                    "bind": "/open5gs/install/etc/open5gs",
                    "mode": "rw",
                },
                "/etc/timezone": {
                    "bind": "/etc/timezone",
                    "mode": "ro",
                },
                "/etc/localtime": {
                    "bind": "/etc/localtime",
                    "mode": "ro",
                },
            },
        },
    )

    # info("*** Adding Host for EPC UP\n")
    # env["COMPONENT_NAME"]="up"
    # up = net.addDockerHost(
    #     "up",
    #     dimage="o5gs_epc",
    #     ip="192.168.0.112/24",
    #     # dcmd="",
    #     dcmd="bash /open5gs/install/etc/open5gs/temp/epc_up.sh",
    #     docker_args={
    #         "environment": env,
    #         "volumes": {
    #             prj_folder + "/epclog": {
    #                 "bind": "/open5gs/install/var/log/open5gs",
    #                 "mode": "rw",
    #             },
    #             prj_folder + "/open5gs/config": {
    #                 "bind": "/open5gs/install/etc/open5gs/temp",
    #                 "mode": "rw",
    #             },
    #             "/etc/timezone": {
    #                 "bind": "/etc/timezone",
    #                 "mode": "ro",
    #             },
    #             "/etc/localtime": {
    #                 "bind": "/etc/localtime",
    #                 "mode": "ro",
    #             },
    #         },
    #         "cap_add": ["NET_ADMIN"],
    #         "sysctls": {"net.ipv4.ip_forward": 1},
    #         "devices": "/dev/net/tun:/dev/net/tun:rwm"
    #     },
    # )

    info("*** Adding SRSENB\n")
    env["COMPONENT_NAME"]="srsenb"
    enb = net.addDockerHost(
        "srsenb", 
        #ip=IPS["enb"],
        dimage="srsran",
        ip="10.80.95.0/24",
        dcmd="bash /home/vagrant/comnetsemu_deploy_4g/srsran/config/enb.sh",
        docker_args={
            "environment": env,
            "volumes": {
                prj_folder + "srsran/config:/etc/srsran:ro",
                prj_folder + "/srslog:/tmp/srsran_logs",
                "/etc/timezone:/etc/timezone:ro",
                "/etc/localtime:/etc/localtime:ro",
            },
            "cap_add": ["NET_ADMIN"],
            "devices": "/dev/net/tun:/dev/net/tun:rwm"
        },
    )

    info("*** Adding SRSUE\n")
    env["COMPONENT_NAME"]="srsue"
    ue = net.addDockerHost(
        "srsue", 
        #ip="10.80.97.3",
        dimage="srsran",
        ip="10.80.97.0/24",
        # dcmd="",
        docker_args={
            "environment": env,
            "volumes": {
                prj_folder + "srsran/config:/etc/srsran:ro",
                prj_folder + "/srslog:/tmp/srsran_logs",
                "/etc/timezone:/etc/timezone:ro",
                "/etc/localtime:/etc/localtime:ro",
            },
            "cap_add": ["NET_ADMIN"],
            "devices": "/dev/net/tun:/dev/net/tun:rwm"
        },
        _ue_cmd = [
        "--rf.device_name=zmq",
        f"--rf.device_args='id=ue,fail_on_disconnect=true,tx_port=tcp://*:2001,rx_port=tcp://{IPS['enb']}:2000,base_srate=23.04e6'",
        "--log.all_level=info",
        "--log.filename=/tmp/srsran_logs/ue.log",
        ">",
        "/proc/1/fd/1",
        "2>&1",
        "&",
        ]
        cmds[ue] = " ".join(_ue_cmd)
        #dcmd="bash /mnt/ueransim/open5gs_gnb_init.sh",
    )


    info("*** Add controller\n")
    net.addController("c0")

    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    info("*** Adding links\n")
    net.addLink(s1,  s2, bw=1000, delay="10ms", intfName1="s1-s2",  intfName2="s2-s1")
    net.addLink(s2,  s3, bw=1000, delay="50ms", intfName1="s2-s3",  intfName2="s3-s2")
    
    net.addLink(ue,  s1, bw=1000, delay="1ms", intfName1="ue-s1",  intfName2="s1-ue")
    net.addLink(enb, s1, bw=1000, delay="1ms", intfName1="enb-s1", intfName2="s1-enb")

    net.addLink(cp,  s1, bw=1000, delay="1ms", intfName1="cp-s1",  intfName2="s1-cp")
    net.addLink(up, s2, bw=1000, delay="1ms", intfName1="up-s2", intfName2="s2-up")
    

    info("\n*** Starting network\n")
    net.start()

    if not AUTOTEST_MODE:
        # spawnXtermDocker("open5gs")
        # spawnXtermDocker("gnb")
        CLI(net)

    net.stop()
