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
from mininet.link import TCLink, TCIntf
from mininet import log
from mininet.log import info, setLogLevel
from mininet.node import Controller, OVSBridge
from mininet.topo import Topo

root_directory="/home/vagrant/comnetsemu_deploy_4g"
mongodb_directory="/home/vagrant/mongodbdata"


if __name__ == "__main__":

    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")
    

    env = dict()
    
    net = Containernet(controller=Controller, link=TCLink, waitConnected=True)
    #net = Containernet(controller=Controller, ipBase="192.168.56.0/24", link=TCLink, waitConnected=True)

    cmds: Dict[DockerHost, str] = {}
    hardcoded_ips: List[Dict[str, str]] = []

    info("*** Adding Host for open5gs EPC\n")
    epc = net.addDockerHost(
        "epc",
        dimage="o5gs_epc",
        ip="192.168.0.10/24",
        # dcmd="",
        dcmd="bash /open5gs/install/etc/open5gs/epc.sh",
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
            "devices": ["/dev/net/tun"],
            "cap_add": ["SYS_NICE", "NET_ADMIN"],
        },
    )

    info("*** Adding Host for SRSRAN ENB\n")
    enb = net.addDockerHost(
        "srsenb",
        #ip=IPS["enb"],
        dimage="srsran3",
        ip="192.168.0.20/24",
        # dcmd="",
        docker_args={
            "volumes": {
                root_directory + "/srsran/config": {
                    "bind": "/etc/srsran",
                    "mode": "rw",
                },
                root_directory + "/srslogs": {
                    "bind": "/tmp/srsran_logs",
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
            "cap_add": ["SYS_NICE"],
            #"sysctls": {"net.ipv4.ip_forward": 1},
        },
        #dcmd="bash /etc/srsran/enb.sh",
    )

    info("*** Adding Host for SRSRAN UE\n")
    ue = net.addDockerHost(
        "srsue",
        #ip=IPS["enb"],
        dimage="srsran3",
        ip="192.168.0.21/24",
        # dcmd="",
        #exec_run= ('/etc/srsran/ue.sh'),
        docker_args={
            "volumes": {
                root_directory + "/srsran/config": {
                    "bind": "/etc/srsran",
                    "mode": "rw",
                },
                root_directory + "/srslogs": {
                    "bind": "/tmp/srsran_logs",
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
            "devices": ["/dev/net/tun"],
            "cap_add": ["SYS_NICE", "NET_ADMIN"],
        },
        #dcmd="bash /etc/srsran/ue.sh",
    )

    enbcmd = [
        "srsenb",
        f"--enb.mme_addr=127.0.0.2",
        f"--enb.gtp_bind_addr=127.0.0.2",
        f"--enb.s1c_bind_addr=127.0.0.2",
        "--rf.device_name=zmq",
        f"--rf.device_args='id=enb,fail_on_disconnect=true,tx_port=tcp://*:2000,rx_port=tcp://192.168.0.21:2001,base_srate=23.04e6'",
        "--enb_files.sib_config=/etc/srsran/sib.conf",
        "--log.all_level=info",
        "--log.filename=/tmp/srsran_logs/enb.log",
        ">",
        "/proc/1/fd/1",
        "2>&1",
        "&",
    ]
    cmds[enb] = " ".join(enbcmd)

    uecmd = [
        "srsue",
        "--rf.device_name=zmq",
        f"--rf.device_args='id=ue,fail_on_disconnect=true,tx_port=tcp://*:2001,rx_port=tcp://192.168.0.20:2000,base_srate=23.04e6'",
        "--log.all_level=info",
        "--log.filename=/tmp/srsran_logs/ue.log",
        ">",
        "/proc/1/fd/1",
        "2>&1",
        "&",
    ]
    cmds[ue] = " ".join(uecmd)

    for host in cmds:
        log.debug(f"::: Running cmd in container ({host.name}): {cmds[host]}\n")
        host.cmd(cmds[host])
        time.sleep(1)

    for host in net.hosts:
        proc = subprocess.Popen(
            [
                "gnome-terminal",
                f"--display={os.environ['DISPLAY']}",
                "--disable-factory",
                "--",
                "docker",
                "logs",
                "-f",
                host.name,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log.debug(f"::: Spawning terminal with {proc.args}")


    info("*** Add controller\n")
    net.addController("c0")

    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    info("*** Adding links\n")
    net.addLink(s1,  s2, bw=1000, delay="1ms", intfName1="s1-s2",  intfName2="s2-s1")
    net.addLink(s2,  s3, bw=1000, delay="1ms", intfName1="s2-s3",  intfName2="s3-s2")
    
    net.addLink(ue,  s1, bw=1000, delay="1ms", intfName1="ue-s1",  intfName2="s1-ue")
    net.addLink(enb, s2, bw=1000, delay="1ms", intfName1="enb-s2", intfName2="s2-enb")
    net.addLink(epc, s3, bw=1000, delay="1ms", intfName1="epc-s3", intfName2="s3-epc")
    
    info("\n*** Starting network\n")
    net.start()

if not AUTOTEST_MODE:
    CLI(net)
    net.stop()
