import socket
import tornado

PORT = 8080

def tcp_server():
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
        # The decode() function converts the bytes data to a string.
        data = client_socket.recv(1024).decode()
        print(f"Received data: {data}")

        # The send() function sends data to the client. The parameter is the data to send. The return value is the number of bytes sent.
        client_socket.send(f"back to you {data}".encode())

        client_socket.close()

def tcp_client():
    # create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    client_socket.connect(('localhost',PORT))
    

    # message = input("Enter a message: ")
    client_socket.send("hello server".encode())
    response = client_socket.recv(1024).decode()
    print(f"Received from the server: {response}")
    
    client_socket.close()
    
def udp_server():
    udp_svr_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_svr_socket.bind(('localhost',PORT))
    
    while True:
        data, client_address = udp_svr_socket.recvfrom(1024)
        print(f"Received data from: {client_address}")
        print(f"Received data: {data.decode()}")
        udp_svr_socket.sendto("back to you".encode(), client_address)
    
def udp_client():
    udp_cli_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_cli_socket.sendto("hello form UDP client".encode(), ('localhost',PORT))
    
    response, svr_address = udp_cli_socket.recvfrom(1024)
    print(f"{response.decode()} from {svr_address}") 

# tcp_client()
# udp_client()
udp_server()


#  Websockets

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("Connection opened")

    def on_close(self):
        print("Connection closed")

    def on_message(self, message):
        print("received: ", message)
        
        
if __name__ == "__main__":
    app = tornado.web.Application([(r'/websocket', WSHandler)])
                                    
                                    
    app.listen(PORT,"localhost")
    tornado.ioloop.IOLoop.current().start()