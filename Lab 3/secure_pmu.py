import argparse
import ssl
import socket
from pathlib import Path
import re
import time

def main():
    parser = argparse.ArgumentParser(description='Secure PMU TCP server (TLS over IPv4, localhost)')
    parser.add_argument('port', type=int, help='The port that will be used by both PDC and PMU.')
    parser.add_argument('certificate', type=Path, help='The path to your signed certificate (.crt).')
    parser.add_argument('key', type=Path, help='The path to your secret key (CAMIPRO_key.pem).')
    args = parser.parse_args()
    verify_arguments(args)

    srv_sock, context = get_secure_socket(args.port, args.certificate, args.key)
    wait_for_clients(srv_sock, context)

def verify_arguments(args):
    if not (0 <= args.port <= 65535):
        print("Invalid port number. Port must be between 0 and 65535.")
        exit(1)
    if not args.key.exists():
        print("key file doesn't exist")
        exit(1)
    if not args.certificate.exists():
        print("certificate file doesn't exist")
        exit(1)

def get_secure_socket(port, certificate, key):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=str(certificate), keyfile=str(key))

    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.bind(('127.0.0.1', port))
    srv_sock.listen(5)
    return srv_sock, context

def manage_client(stream):
    try:
        data = stream.recv(1024)
    except Exception:
        return

    if not data:
        return

    text = data.decode(errors='ignore').strip()
    match = re.fullmatch(r'CMD_short:(\d+)', text)
    if not match:
        stream.close()
        return

    delay = int(match.group(1))
    print(delay)
    messages_count = 12         

    for i in range(messages_count):
        line = f"This is PMU data {i}\n"
        stream.sendall(line.encode())
        if delay >= 0:
            time.sleep(delay)
    
    stream.close()

def wait_for_clients(srv_sock, context):
    while True:
        client_sock, fromaddr = srv_sock.accept()
        stream = None
        try:
            stream = context.wrap_socket(client_sock, server_side=True)
            manage_client(stream)
        finally:
            try:
                if stream is not None:
                    stream.shutdown(socket.SHUT_RDWR)
                    stream.close()
            except Exception:
                pass
            try:
                client_sock.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
