#!/usr/bin/python

"Importing Libraries"
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def starNetwork(N):
    net = Mininet()
    net.addController('c0')

    router = net.addHost('router', ip='10.10.10.1/24')

    for i in range(2, N+2):
        host = net.addHost(f'h{i}', ip=f'10.10.10.{i}/24')
        switch = net.addSwitch(f's{i}')
        net.addLink(host, switch)
        net.addLink(router, switch)

    net.start()

    router.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')

    for i in range(2, N+2):
        h = net.get(f'h{i}')
        h.cmd('ip route add default via 10.10.10.1')

    loss = net.pingAll()
    print(f"[Star N={N}] Packet loss: {loss}%")

    net.stop()

#!/usr/bin/python

"Importing Libraries"
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

# helper to generate unique /24 subnets
def ipgen():
    base = 10
    subnet = 1
    while True:
        yield f"{base}.{subnet}.0."
        subnet += 1

def binaryTree(depth):
    net = Mininet()
    net.addController('c0')
    ips = ipgen()

    # dictionary to store router names and their subnets
    routers = {}

    # recursive function to build the tree
    def build(level, idx):
        name = f"r{level}_{idx}"
        if name not in routers:
            subnet = next(ips)
            routers[name] = subnet
            router = net.addHost(name, ip=f"{subnet}1/24")
            router.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
        else:
            router = net.get(name)
        return router

    # build routers and connect them
    def buildTree(level, idx, maxDepth):
        parent = build(level, idx)
        if level < maxDepth:  # still building routers
            left = buildTree(level+1, 2*idx, maxDepth)
            right = buildTree(level+1, 2*idx+1, maxDepth)
            swL = net.addSwitch(f"s{level}_{idx}l")
            swR = net.addSwitch(f"s{level}_{idx}r")
            net.addLink(parent, swL)
            net.addLink(left, swL)
            net.addLink(parent, swR)
            net.addLink(right, swR)
        else:  # leaves → attach hosts
            # left host
            subnetL = next(ips)
            hostL = net.addHost(f"h{2*idx}", ip=f"{subnetL}2/24")
            swL = net.addSwitch(f"s{level}_{idx}l")
            net.addLink(parent, swL)
            net.addLink(hostL, swL)
            hostL.cmd(f"ip route add default via {subnetL}1")

            # right host
            subnetR = next(ips)
            hostR = net.addHost(f"h{2*idx+1}", ip=f"{subnetR}2/24")
            swR = net.addSwitch(f"s{level}_{idx}r")
            net.addLink(parent, swR)
            net.addLink(hostR, swR)
            hostR.cmd(f"ip route add default via {subnetR}1")
        return parent

    # build tree of given depth
    buildTree(1, 1, depth)

    net.start()

    # benchmark: connectivity
    loss = net.pingAll()
    print(f"[Binary Tree depth={depth}] Packet loss: {loss}%")

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    # change depth as needed (depth=2 → 4 hosts, depth=3 → 8 hosts, etc.)
    binaryTree(depth=2)


def buildTree(net, depth, index=1, parent=None, parentIP=None):
    """
    Recursively build a full binary tree of routers.
    depth = how many levels (leaf level = hosts)
    index = unique index to name nodes
    parent = parent router (if any)
    parentIP = IP address to use at parent side
    """
    name = f'r{index}'
    router = net.addHost(name, cls=LinuxRouter, ip=None)

    if parent:
        # connect router to parent
        net.addLink(parent, router)
        # IPs assigned after net.start()

    if depth == 1:
        # leaf → add a host
        h = net.addHost(f'h{index}', ip=None)
        net.addLink(router, h)

    else:
        # recurse left and right children
        buildTree(net, depth-1, index*2, router)
        buildTree(net, depth-1, index*2+1, router)

    return router

def binaryTree(depth=3):
    net = Mininet(controller=None, autoSetMacs=True, autoStaticArp=True)

    # build the tree
    root = buildTree(net, depth)

    net.start()

    # Assign IP addresses
    counter = 1
    for link in net.links:
        n1, n2 = link.intf1.node, link.intf2.node
        ip1 = f'10.0.{counter}.1/24'
        ip2 = f'10.0.{counter}.2/24'
        link.intf1.setIP(ip1)
        link.intf2.setIP(ip2)
        counter += 1

    # Configure default routes for hosts (via their router)
    for host in net.hosts:
        if host.name.startswith('h'):
            # take first interface's peer IP as default gateway
            intf = host.intf()
            gw = intf.link.intf1.IP() if intf.link.intf1.node != host else intf.link.intf2.IP()
            host.cmd(f'ip route add default via {gw}')

    # Benchmark: run pingall
    print("*** Running pingAll test")
    loss = net.pingAll()
    print(f"*** Packet loss: {loss}%")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    binaryTree(depth=3)   # try depth 2,3,4


if __name__ == '__main__':
    for N in [2, 4, 6, 8, 10]:
        starNetwork(N)