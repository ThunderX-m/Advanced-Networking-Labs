import websocket
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

    websock = connect_to_server(args)
    execute_command(websock, args.command)

def verify_arguments(args):
    if not (0 <= args.port <= 65535):
        print("Invalid port number. Port must be between 0 and 65535.")
        exit(1)
    if args.command not in ['CMD_short:0', 'CMD_short:1', 'CMD_floodme']:
        print("Invalid command.")
        exit(1)
    return True

def connect_to_server(args):
    try:
        websock = websocket.create_connection(f"ws://{args.server}:{args.port}")
    except Exception as e:
        print("Connection error:", e)
        websock.close()
        exit(1)
    return websock

def execute_command(websock, command):
    try:
        websock.send(command)
        recv_data(websock, command == 'CMD_floodme')
    except Exception as e:
        print("Error during communication:", e)
    finally:
        websock.close()

def recv_data(websock, floodme=False):
    count_recv = 0
    while True:
        message = websock.recv()
        count_recv += 1
        if not message:
            break
        if floodme:
            print(message)
        else:
            for line in get_lines(message):
                print(line)
    print(f"Total calls to recv: {count_recv}")

def get_lines(text):
    if isinstance(text, bytes):
        text = text.decode(errors='ignore')
    return re.findall(r'This is PMU data \d+', text)

if __name__ == "__main__":
    main()