import argparse
import socket

def main():
    parser = argparse.ArgumentParser(description="Swisscom multicast sender")
    parser.add_argument("group", type=str, help="Multicast group address")
    parser.add_argument("port", type=int, help="Multicast port number")
    parser.add_argument("sciper", type=str, help="Your 6-digit SCIPER (Camipro) number")
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    print(f"Sending messages to multicast group {args.group}:{args.port} as SCIPER {args.sciper}")
    print("Type your messages and press Enter to send (Ctrl+C to quit)\n")

    while True:
        message = input("").strip()
        if not message:
            continue
        if message == "exit":
            sock.close()
            exit()
        payload = args.sciper + " : " + message
        sock.sendto(payload.encode(), (args.group, args.port))

if __name__ == "__main__":
    main()
