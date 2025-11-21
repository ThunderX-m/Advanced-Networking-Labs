import argparse
import socket
import struct

def main():
    parser = argparse.ArgumentParser(description='PDC TCP client')
    parser.add_argument('group', type=str, help='The multicast group address on which to listen.')
    parser.add_argument('port', type=int, help='The port number on which to listen.')
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', args.port))
    join_the_multicast_group(sock, args.group)
    listen(sock, args.group, args.port)

def join_the_multicast_group(sock, group):
    group = socket.inet_aton(group)
    mreq = struct.pack("4s4s", group, socket.inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def listen(sock, group, port):
    print(f"Listening on multicast group {group}:{port}")
    while True:
        data, addr = sock.recvfrom(1024)
        print(data.decode(), flush=True)


if __name__ == "__main__":
    main()