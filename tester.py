from digs.data_node import data_handler
import json
import socket
#print(data_handler.get_data_chunk("DataFiles/DataNodes/testFasta.data", 236970, 236981))
def main():
    host = "localhost"
    port = 5001

    str = 'chunk '
    data = {}
    data['parameters'] = "DataFiles/DataNodes/testFasta.data 236970 236981"
    str = str + json.dumps(data)
    print(str)
    ServerSocket = socket.socket()
    ServerSocket.connect((host, port))

    ServerSocket.send(str.encode())
    ServerSocket.close()



if __name__ == '__main__':
    main()