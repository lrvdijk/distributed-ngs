import sys
import socket
import os
import time
import json

from digs.manager.models import DataType

# why cannot i commit anymore?
def main():
    hash = 11111
    str1 = 'store_data '
    data = {}
    data['hash'] = hash
    data['size'] = 5953039
    data['type'] = 'shotgun'
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
    parts = data.decode().strip().split(maxsplit=1)
    result = json.loads(parts[1])
    print(result['socket'])
    cmd = "rsync -avz --append-verify --info=progress2 "
    local_path = "/home/dwarrel/Courses/Distributed/distributed-ngs/DataFiles/ClientData/AAAE "
    remote_path = "/home/dwarrel/Courses/Distributed/distributed-ngs/DataFiles/DataNodes/" + str(result['socket'])
    rsync = cmd + local_path + remote_path
    err = os.system(rsync)
    print(err)
    if err is 0:
        print("No error found! good job")
        str1 = 'store_data_done '
        data = {}
        data['hash'] = hash
        str1 = str1 + json.dumps(data) + '\n'
        family, type, proto, _, addr = socket.getaddrinfo(
            host, port, proto=socket.IPPROTO_TCP)[0]
        # print(str(HeartBeat(time=time.time())))
        sock = socket.socket(family, type, proto)
        sock.settimeout(5)
        sock.connect(addr)
        sock.sendall(str1.encode())

    else:
        print("Error rsync not complete! try again!")



if __name__ == '__main__':
    main()
