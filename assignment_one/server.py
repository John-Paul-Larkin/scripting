
import socket

PORT  = 8080

def tcp_server():
    # create the socket object
    server_socket = socket.socket(socket.AF_INET, 
                                socket.SOCK_STREAM )
    # book a port
    server_socket.bind(('localhost',PORT))

    # listen for incoming connection
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        data = client_socket.recv(1024).decode()
        print(f"Received from client {data}")
        client_socket.send(f"back to you! {data}".encode())
        
        client_socket.close()
        
        
if __name__ == "__main__":
    tcp_server() 