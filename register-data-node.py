import sys
import socket
import os
import time
import json

from node_settings import IP, TOTAL, FREE

def main():
    str1 = 'register_data_node '
    data = {}
    data['ip'] = IP
    data['socket'] = 5001
    data['free_space'] = FREE
    data['disk_space'] = TOTAL
    data['root_path'] = '/distributed/dataFiles'
    str1 = str1 + json.dumps(data) + '\n'
    print(str1)

    if len(sys.argv) == 2:
        host = sys.argv[0]
        port = int(sys.argv[1])
    else:
        host = "130.211.67.58"
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
    parts = data.decode().strip().split(maxsplit=1)
    result = json.loads(parts[1])
    print(result)
    print(parts[0])

if __name__ == '__main__':
    main()
