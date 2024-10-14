import socket

PORT = 8080
# The socket() function creates a new socket object. The first parameter is the address family, which is AF_INET for IPv4 and AF_INET6 for IPv6. The second parameter is the socket type, which is SOCK_STREAM for TCP and SOCK_DGRAM for UDP.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# book a port
server_socket.bind(('localhost',PORT))

# 5 is the maximum number of queued connections. When the server is busy and cannot accept new connections, the operating system will queue up to 5 connections before refusing new connections.
# 5 is the default
server_socket.listen(5)

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    # The recv() function receives data from the client. The parameter is the maximum number of bytes to receive. The return value is the data received from the client.
    data = client_socket.recv(1024)
