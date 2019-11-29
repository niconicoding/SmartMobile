import socket
import sys
from time import sleep
port = int(sys.argv[1])
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", port))
server_socket.listen(5)


print ("TCPServer Waiting for client on port "+str(port))

first_client_socket = 0
first_address = 0
second_client_socket = 0
second_address = 0


def errorProcessing(socket):
     print("E: Original Mobile Messaage Time Out. I Will Turn On Alternative Mobile")
     socket.send("Turn On".encode())


while True:
    clients = [0,0]
    while clients[0] != 1 or clients[1] != 1:

         socket, address = server_socket.accept()
         data = socket.recv(512).decode()
         if data == 'first':
              first_client_socket = socket
              first_address = address
              clients[0] = 1
              print("Main Board Comming")
         else :
              second_client_socket = socket
              second_address = address
              clients[1] = 1
              print("Alternative Board Comming")

    print ("I got a connection")
    first_client_socket.settimeout(10)

    while True:
        try:
            data = first_client_socket.recv(512).decode()
            if len(data) == 0:
                 errorProcessing(second_client_socket)
                 break
        except:
            errorProcessing(second_client_socket)
            break

server_socket.close()
print("SOCKET closed... END")
