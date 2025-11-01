#usage python3 client.py command path-to-CA-cert
import socket
import ssl
import pprint
from datetime import datetime
from time import sleep
import subprocess
import re
import sys

HOST = '127.0.0.1'
PORT = 5003
BUFFER_SIZE = 1024

if len(sys.argv) != 3:
    print('usage: %s <command> <path to CA certificate>' % sys.argv[0])
    sys.exit(1)

d = sys.argv[1]
filecert = sys.argv[2]
ssl_s1 = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_INET, socket.SOCK_STREAM):
	af, socktype, proto, canonname, sa = res
	s1 = socket.socket(af, socktype, proto)
	ssl_s1 = ssl.wrap_socket(s1, ca_certs=filecert, cert_reqs=ssl.CERT_REQUIRED)
	ssl_s1.connect(sa)
	print('ssl_s1: ',ssl_s1)

message = d
ssl_s1.send(message.encode('utf-8'))
print("sending:", message)
i=15

RETRIES_1 = 100
for i in range(0, RETRIES_1):
	print('User 1 received:', ssl_s1.recv(BUFFER_SIZE).decode('utf-8'), '\n')
	sleep(1)
while True:
    pass
