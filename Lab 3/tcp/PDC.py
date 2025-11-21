import argparse
import socket
import re

def main():
    parser = argparse.ArgumentParser(description='PDC TCP client')
    parser.add_argument('server', type=str, help=' IPv4 address of the server or its domain name.')
    parser.add_argument('port', type=int, help=' Port number of the server.')
    parser.add_argument('command', type=str, help='Command to send to the server, i.e. either CMD_short:0 or CMD_short:1 or CMD_floodme (see later).')
    args = parser.parse_args()
    verify_arguments(args)

    sock = connect_to_server(args)
    execute_command(sock, args.command)

def verify_arguments(args):
    if not (0 <= args.port <= 65535):
        print("Invalid port number. Port must be between 0 and 65535.")
        exit(1)
    if args.command not in ['CMD_short:0', 'CMD_short:1', 'CMD_floodme']:
        print("Invalid command.")
        exit(1)
    return True

def connect_to_server(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((args.server, args.port))
    except Exception as e:
        print("Connection error:", e)
        sock.close()
        exit(1)
    return sock

def execute_command(sock, command):
    try:
        sock.sendall(command.encode())
        recv_data(sock, command == 'CMD_floodme')

    except Exception as e:
        print("Error during communication:", e)
    finally:
        sock.close()

def recv_data(sock, floodme=False):
    count_recv = 0
    while True:
        data = sock.recv(4096)
        count_recv += 1
        if not data:
            break
        if floodme:
            print(data.decode())
        else:
            for line in get_lines(data.decode()):
                print(line)
    print(f"Total calls to recv: {count_recv}")

def get_lines(text):
    return re.findall(r'This is PMU data \d+', text)

if __name__ == "__main__":
    main()