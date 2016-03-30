from digs.data_node import handlers
import json
import socket
#print(data_handler.get_data_chunk("DataFiles/DataNodes/testFasta.data", 236970, 236981))
def main():
    host = "localhost"
    port = 5001

    str = 'get_data_chunk '
    data = {}
    data['file_path'] = "DataFiles/DataNodes/testFasta.data"
    data['chunk_start'] = 236970
    data['chunk_end'] = 236981
    str = str + json.dumps(data)
    print(str)
    ServerSocket = socket.socket()
    ServerSocket.connect((host, port))

    ServerSocket.send(str.encode())
    #
    # MSGLEN = 3000
    # chunks = []
    # bytes_recd = 0
    # while bytes_recd < MSGLEN:
    #     chunk = ServerSocket.recv(min(MSGLEN - bytes_recd, 1024))
    #     if chunk == b'':
    #         print("Connection lost")
    #         break
    #     chunks.append(chunk)
    #     bytes_recd = bytes_recd + len(chunk)
    #
    # result = b''.join(chunks)
    # print("Result: " + result.decode())
    ServerSocket.close()



if __name__ == '__main__':
    main()