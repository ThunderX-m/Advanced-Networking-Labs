#! /usr/bin/env python3.5

import socket, struct, sys, time

MCAST_GRP = ''
MCAST_PORT = 0
file = None
interval = 1

if len(sys.argv) != 5:
    print('usage: %s <mcast_address> <port> <text_file> <interval>' % sys.argv[0])
    sys.exit(1)

try:
    MCAST_GRP = sys.argv[1]
    MCAST_PORT = int(sys.argv[2])
    tfile = open(sys.argv[3], 'r')
    interval = float(sys.argv[4])
except:
    print('Invalid parameters')
    print('usage: %s <mcast_address> <port> <text_file> <interval>' % sys.argv[0])
    sys.exit(2)
    
cl_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ttl = struct.pack('b', 10)
cl_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

while True:
    for mesg in tfile:
        mesg = mesg.rstrip()
        cl_sock.sendto(('swcmTV'+mesg).encode(), (MCAST_GRP, MCAST_PORT))
        time.sleep(interval)
    cl_sock.sendto(('swcmTV'+'RWND...').encode(), (MCAST_GRP, MCAST_PORT))
    tfile.close()
    time.sleep(3*interval)
    tfile = open(sys.argv[3], 'r')

cl_sock.close()
