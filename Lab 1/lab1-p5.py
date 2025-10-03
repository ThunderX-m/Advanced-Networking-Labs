#!/usr/bin/python

"Importing Libraries"
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def starNetwork(N):
    net = Mininet()
    net.addController( 'c0' )
    router = net.addHost('router', ip='10.10.10.1/24')
    for i in range(2,N+2):
        host = net.addHost( f'h{i}', ip=f'10.10.10.{i}/24')
        switch = net.addSwitch( f's{i}' )
        net.addLink( host, switch )
        net.addLink( router, switch )
        host.cmd('ip route add default via 10.10.10.1')

    router.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    net.start()

if __name__ == '__main__':
    setLogLevel( 'info' )
    starNetwork(10)

