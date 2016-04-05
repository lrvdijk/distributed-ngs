import sys
import socket
import time

from digs.common.actions import HeartBeat


def main():
    if len(sys.argv) == 2:
        host = sys.argv[0]
        port = int(sys.argv[1])
    else:
        host = "127.0.0.1"
        port = 31415

    family, type, proto, _, addr = socket.getaddrinfo(
        host, port, proto=socket.IPPROTO_TCP)[0]

    sock = socket.socket(family, type, proto)
    sock.settimeout(5)
    sock.connect(addr)
    sock.sendall(str(HeartBeat(time=time.time())).encode())

    data = sock.recv(4096)
    print("[*] Received:", data)

    sock.close()

if __name__ == '__main__':
    main()
