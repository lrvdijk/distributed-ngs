from digs.data_node import data_handler
import socket
#print(data_handler.get_data_chunk("DataFiles/DataNodes/testFasta.data", 236970, 236981))
def main():
    host = "localhost"
    port = 5000

    ServerSocket = socket.socket()
    ServerSocket.connect((host, port))

    ServerSocket.send("LETSDOTHEHELLO".encode())
    ServerSocket.close()


if __name__ == '__main__':
    main()