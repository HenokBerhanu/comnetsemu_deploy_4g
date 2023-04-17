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
    h1 = net.addHost( 'h1', ip="10.0.0.1" )
    h3 = net.addHost( 'h3', ip="10.0.0.3" )
    s1 = net.addSwitch( 's1')
    s3 = net.addSwitch( 's3')
    c0 = net.addController('c0', controller=RemoteController, ip='192.168.56.101', port=6633 )

    print("*** Adding Link")
    net.addLink(h1,s1)
    net.addLink(h3,s3)
    net.addLink(s1,s3)

    print("*** Starting network")
    c0.start()
    s1.start([c0])
    s3.start([c0])
    s1.cmd("ip link add s1-gre1 type gretap local 192.168.56.101 remote 192.168.56.102 ttl 64")
    s1.cmd("ip link set s1-gre1 up")
    Intf("s1-gre1", node=s1)

    s3.cmd("ip link add s3-gre1 type gretap local 192.168.56.101 remote 192.168.56.102 ttl 64")
    s3.cmd("ip link set s3-gre1 up")
    Intf("s3-gre1", node=s3)

    print("*** Running CLI")
    net.start()
    CLI( net )

    print("*** Stopping network")
    s1.cmd("ip link del dev s1-gre1")
    s3.cmd("ip link del dev s3-gre1")
    net.stop()

if __name__ == '__main__':

    setLogLevel( 'info' )

    topology()