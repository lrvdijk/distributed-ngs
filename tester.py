import sys
import socket
import time
import json

from digs.common.actions import HeartBeat


def main():
    str1 = 'get_all_data_locs '
    data = {}
    data['file_id'] = 1
    # data['chunk_start'] = 236970
    # data['chunk_end'] = 236981
    str1 = str1 + json.dumps(data) + '\n'
    print(str1)

    if len(sys.argv) == 2:
        host = sys.argv[0]
        port = int(sys.argv[1])
    else:
        host = "127.0.0.1"
        port = 31415

    family, type, proto, _, addr = socket.getaddrinfo(
        host, port, proto=socket.IPPROTO_TCP)[0]
    # print(str(HeartBeat(time=time.time())))
    sock = socket.socket(family, type, proto)
    sock.settimeout(5)
    sock.connect(addr)
    sock.sendall(str1.encode())

    data = sock.recv(4096)
    print("[*] Received:", data)

    sock.close()

if __name__ == '__main__':
    main()
