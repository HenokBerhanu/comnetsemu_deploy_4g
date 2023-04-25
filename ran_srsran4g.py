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


if __name__ == "__main__":

    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")
    

    env = dict()
    
    net = Containernet(controller=Controller, link=TCLink, waitConnected=True)

    cmds: Dict[DockerHost, str] = {}
    hardcoded_ips: List[Dict[str, str]] = []

    info("*** Adding Host for SRSRAN ENB\n")
    env["COMPONENT_NAME"]="srsenb"
    srsenb = net.addDockerHost(
        "srsenb",
        dimage="srsran3",
        ip="192.168.0.20/24",
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
        ip="192.168.0.30/24",
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
    c0 = net.addController('c0', controller=RemoteController, ip='192.168.56.101', port=6633 )

    info("*** Adding switch\n")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    info("*** Adding links\n")
    net.addLink(s1,  s2, bw=1000, delay="1ms", intfName1="s1-s2",  intfName2="s2-s1")
    net.addLink(srsue,  s1, bw=1000, delay="1ms", intfName1="srsue-s1",  intfName2="s1-srsue")
    net.addLink(srsenb, s2, bw=1000, delay="1ms", intfName1="srsenb-s2", intfName2="s2-srsenb")
    
    info("\n*** Starting network\n")
    c0.start()
    s1.start([c0])
    s2.start([c0])
    s1.cmd("ip link add s1-gre1 type gretap local 192.168.56.101 remote 192.168.56.102 ttl 64")
    s1.cmd("ip link set s1-gre1 up")
    Intf("s1-gre1", node=s1)

    s2.cmd("ip link add s2-gre1 type gretap local 192.168.56.101 remote 192.168.56.102 ttl 64")
    s2.cmd("ip link set s2-gre1 up")
    Intf("s2-gre1", node=s2)

    info("\n*** Running CLI\n")
    net.start()

if not AUTOTEST_MODE:
    CLI(net)
    s1.cmd("ip link del dev s1-gre1")
    s2.cmd("ip link del dev s2-gre1")
    net.stop()
