#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import  Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink, Intf

def topology():

    "Create a network."

    net = Mininet( controller=Controller, link=TCLink, switch=OVSKernelSwitch )
    print("*** Creating nodes")
    h2 = net.addHost( 'h2', ip="10.0.0.2" )
    s2 = net.addSwitch( 's2')
    c0 = net.addController('c0', controller=RemoteController, ip='192.168.56.101', port=6633 )

    print("*** Adding Link")
    net.addLink(h2,s2)

    print("*** Starting network")
    c0.start()
    s2.start([c0])
    s2.cmd("ip link add s2-gre1 type gretap local 192.168.56.102 remote 192.168.56.101 ttl 64")
    s2.cmd("ip link set s2-gre1 up")
    Intf("s2-gre1", node=s2)


    print("*** Running CLI")
    net.start()
    CLI( net )

    print("*** Stopping network")
    s2.cmd("ip link del dev s2-gre1")
    net.stop()

if __name__ == '__main__':

    setLogLevel( 'info' )

    topology()