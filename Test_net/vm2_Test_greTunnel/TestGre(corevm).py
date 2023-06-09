#!/usr/bin/python

# https://www.google.com/search?q=linux+gre+tunnels+with+mininet&oq=linux+gre+tunnels+with+mininet&aqs=chrome.0.69i59j0i546l2.10984j0j7&sourceid=chrome&ie=UTF-8
# https://csie1.nqu.edu.tw/smallko/sdn/vm2vm_gre.htm
# https://techandtrains.com/2014/01/25/using-linux-gre-tunnels-to-connect-two-mininet-networks/
# https://techandtrains.com/2014/01/20/connecting-two-mininet-networks-with-gre-tunnel-part-2/
# sudo controller -v ptcp:6633

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