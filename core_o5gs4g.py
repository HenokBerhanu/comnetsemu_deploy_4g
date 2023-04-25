import atexit
import os
import shlex
import signal
import subprocess
import time
from typing import Dict, List

from comnetsemu.cli import CLI, spawnXtermDocker
from comnetsemu.net import Containernet, VNFManager
from comnetsemu.node import DockerHost
from mininet.link import TCLink, TCIntf, Intf
from mininet import log
from mininet.log import info, setLogLevel
from mininet.node import Controller, RemoteController, OVSBridge, OVSKernelSwitch
from mininet.topo import Topo

root_directory="/home/vagrant/comnetsemu_deploy_4g"
mongodb_directory="/home/vagrant/mongodbdata"


if __name__ == "__main__":

    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")
    

    env = dict()
    
    net = Containernet(controller=Controller, link=TCLink, waitConnected=True)


    info("*** Adding Host for open5gs EPC\n")
    epc = net.addDockerHost(
        "epc",
        dimage="o5gs_epc",
        ip="192.168.0.10/24",
        dcmd = "bash /open5gs/install/etc/open5gs/epc.sh",
        docker_args={
            "ports" : { "3000/tcp": 3000 },
            "volumes": {
                root_directory + "/epclogs": {
                    "bind": "/open5gs/install/var/log/open5gs",
                    "mode": "rw",
                },
                mongodb_directory: {
                    "bind": "/var/lib/mongodb",
                    "mode": "rw",
                },
                root_directory + "/open5gs/config": {
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

    info("*** Add controller\n")
    c0 = net.addController('c0', controller=RemoteController, ip='192.168.56.101', port=6633 )

    info("*** Adding switch\n")
    s3 = net.addSwitch("s3")

    info("*** Adding links\n")
    net.addLink(epc, s3, bw=1000, delay="1ms", intfName1="epc-s3", intfName2="s3-epc")
    
    info("\n*** Starting network\n")
    c0.start()
    s3.start([c0])
    s3.cmd("ip link add s3-gre1 type gretap local 192.168.56.102 remote 192.168.56.101 ttl 64")
    s3.cmd("ip link set s3-gre1 up")
    Intf("s3-gre1", node=s3)

    info("\n*** Running CLI\n")
    net.start()

if not AUTOTEST_MODE:
    CLI(net)
    s3.cmd("ip link del dev s3-gre1")
    net.stop()
