import argparse
import socket
import re

class MySocket():
    def __init__(self, args):
        self.server = args.server
        self.port = args.port
        self.addresses = socket.getaddrinfo(self.server, self.port, 0, socket.SOCK_DGRAM)
        self.sockets = self.get_sockets(self.addresses)
        
    def get_sockets(self, family):
        sockets = []
        for family,_,_,_,sockaddr in self.addresses:
            print(f"Creating socket for {sockaddr}")
            sock = socket.socket(family, socket.SOCK_DGRAM)
            sock.settimeout(1)
            sockets.append((sock, sockaddr))
        return sockets
    
    def send(self, data):
        for sock in self.sockets:
            sock[0].sendto(data, sock[1])

    def recv(self, bufsize):
        data = b""
        for sock in self.sockets:
            print(f"Waiting for data on socket connected to {sock[1]}")
            try:
                data, _ = sock[0].recvfrom(bufsize)
                print(f"Received data from {sock[1]}")
                return data
            except socket.timeout:
                continue
        return data

    def close(self):
        for sock in self.sockets:
            sock[0].close()

def main():
    parser = argparse.ArgumentParser(description='PDC TCP client')
    parser.add_argument('server', type=str, help=' IP address of the server or its domain name.')
    parser.add_argument('port', type=int, help=' Port number of the server.')
    args = parser.parse_args()
    verify_arguments(args)

    sock = MySocket(args)
    command = "RESET:20"
    total_count = 0
    for _ in range(60):
        count = execute_command(sock, command)
        total_count += count
        print(f"count: {count}")
    print("\n--- Results ---")
    print(f"Total count: {total_count}")
    avg_count = total_count / 60
    print(f"Average count: {avg_count}")
    success_prob = 1 / avg_count
    loss_prob = 1 - success_prob
    print(f"Estimated success probability p: {success_prob}")
    print(f"Estimated loss probability: {loss_prob}")

def verify_arguments(args):
    if not (0 <= args.port <= 65535):
        print("Invalid port number. Port must be between 0 and 65535.")
        exit(1)
    return True

def execute_command(sock, command):
        count = 0
        while True:
            count += 1
            sock.send(command.encode())
            if recv_data(sock):
                break
        return count

def recv_data(sock):
    text = sock.recv(1024).decode()
    print(text)
    if re.search(r'OFFSET:\d+', text):
        print("Received OFFSET command, stopping.")
        return True
    return False

if __name__ == "__main__":
    main()