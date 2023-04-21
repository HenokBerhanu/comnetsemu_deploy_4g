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

    info("*** Adding Host for SRSRAN ENB\n")
    env["COMPONENT_NAME"]="srsenb"
    srsenb = net.addDockerHost(
        "srsenb",
        #ip=IPS["enb"],
        dimage="srsran3",
        ip="192.168.0.20/24",
        # dcmd="",
        exec_run = "/etc/srsran/enb.conf",
        #dcmd="bash /etc/srsran/enb.sh",
        docker_args={
            "environment": env,
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
                "/dev": {"bind": "/dev", "mode": "rw"},
            },
            "cap_add": ["NET_ADMIN"],
            "devices": "/dev/net/tun:/dev/net/tun:rwm"
        },
    )

    info("*** Adding Host for SRSRAN UE\n")
    env["COMPONENT_NAME"]="srsue"
    srsue = net.addDockerHost(
        "srsue",
        dimage="srsran3",
        ip="192.168.0.21/24",
        exec_run = "/etc/srsran/ue.conf",
        docker_args={
            "environment": env,
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
                "/dev": {"bind": "/dev", "mode": "rw"},
            },
            "cap_add": ["NET_ADMIN"],
            "devices": "/dev/net/tun:/dev/net/tun:rwm"
        },
    )

    enbcmd = [
        "srsenb",
        "--log.all_level=info",
        "--log.filename=/tmp/srsran_logs/enb.log", ">", "/proc/1/fd/1", "2>&1", "&",
    ]
    cmds[srsenb] = " ".join(enbcmd)

    uecmd = [
        "srsue",
        "--log.all_level=info",
        "--log.filename=/tmp/srsran_logs/ue.log", ">", "/proc/1/fd/1", "2>&1", "&",
    ]
    cmds[srsue] = " ".join(uecmd)

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
    
    net.addLink(srsue,  s1, bw=1000, delay="1ms", intfName1="srsue-s1",  intfName2="s1-srsue")
    net.addLink(srsenb, s2, bw=1000, delay="1ms", intfName1="srsenb-s2", intfName2="s2-srsenb")
    net.addLink(epc, s3, bw=1000, delay="1ms", intfName1="epc-s3", intfName2="s3-epc")
    
    info("\n*** Starting network\n")
    net.start()

if not AUTOTEST_MODE:
    CLI(net)
    net.stop()
