import sys
import socket
import os
import json


def main():
    hash = 11011
    str1 = 'store_data '
    data = {'hash': hash, 'size': 59539, 'type': 'shotgun'}
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

    base_path = os.path.join(os.path.dirname(__file__), 'DataFiles')

    local_path = os.path.join(base_path, 'ClientData', 'AAAE')
    remote_path = os.path.join(base_path, 'DataNodes', str(result['socket']))
    rsync = "{} {} {}".format(cmd, local_path, remote_path)
    err = os.system(rsync)
    print(err)
    if err is 0:
        print("No error found! good job")
        str1 = 'store_data_done '
        data = {'hash': hash}
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
