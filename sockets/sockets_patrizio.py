# for vanilla TCP/UDP sockets
import socket

# for server
import tornado.ioloop
import tornado.websocket

# for the client
import websocket
import threading
import time

# import parser to avoid having to comment and uncomment code
import argparse

PORT = 8080

#################################################
# TCP and UDP sockets
#################################################

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

def tcp_client():
    # create the socket object
    client_socket = socket.socket(socket.AF_INET, 
                                socket.SOCK_STREAM )
    
    client_socket.connect(('localhost',PORT))
    
    client_socket.send("Hello Server!!!!".encode())
    response = client_socket.recv(1024).decode()
    print(f"Received from the server: {response}")
    client_socket.close()

def udp_server():
    udp_svr_socket = socket.socket(
        socket.AF_INET, 
        socket.SOCK_DGRAM )
    udp_svr_socket.bind(('localhost',PORT))

    while True:
        data, client_address = udp_svr_socket.recvfrom(1024)
        print( f"Received data from {client_address}")    
        print( f"\tdata{data.decode()}")    
        udp_svr_socket.sendto("Hello from server",
                              client_address )

def udp_client():
    udp_cli_socket = socket.socket(socket.AF_INET, 
                                socket.SOCK_DGRAM )
    udp_cli_socket.sendto("Hello from UDP client".encode(), 
                        ('localhost',PORT))
    response, svr_address = udp_cli_socket.recvfrom(1024)
    print( f"{response.decode()} from {svr_address}")

#################################################
# Websockets and Tornado
#################################################
class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    def open(self):
        print("Connection opened")
    def on_close(self):
        print("Connection closed")
    def on_message(self, message):
        print("received: ", message)
        self.write_message(f"{message}->back to you")

def create_web_socket_server():
    app = tornado.web.Application([(r'/websocket', WSHandler)])
    app.listen(PORT, "127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()

# This is the old client
def create_client_web_socket():
    ws = websocket.create_connection("ws://127.0.0.1:8080/websocket")
    ws.send("hello server?")
    result = ws.recv()
    print(f"Server says:" + result)

def cli_open(ws):
    print("Connection opened")
    threading.Thread(target=handle_user_input, args=(ws,)).start()


def cli_message(ws, message):
    print(f"server>>{message}")

def start_async_web_socket_client():
    websocket_url = ("ws://127.0.0.1:8080/websocket")
    ws = websocket.WebSocketApp(
         websocket_url,
         on_open=cli_open,
         on_message=cli_message
    )
    client_thread = threading.Thread(target = ws.run_forever() )
    client_thread.daemon = True
    client_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Chat client terminated")   
    return ws

def handle_user_input(ws):
    while True:
        message = input("you>>")
        if message.lower() == 'exit':
            ws.close()
            break
        ws.send(message)
        time.sleep(0.2)

#################################################
# Main
#################################################

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Run the application in server or client mode.")
    parser.add_argument('--mode', choices=["server", "client"],
        required=True,
        help="Run in server mode or client mode"
    )
                        
    parser.add_argument('--type', choices=['websocket', 'tcp', 'udp'],
        required=True,
        help="Choose between websockets, tcp, or udp"
    )
    args = parser.parse_args()
    if args.type == 'tcp':
        if args.mode == "server":
            tcp_server()
        else:
            tcp_client()
    elif args.type == 'websocket':
        if args.mode == "server":
            create_web_socket_server()
        else:
            start_async_web_socket_client()
    elif args.type == 'udp':
        if args.mode == "server":
            udp_server()
        else:
            udp_client()
    else:
        print("Invalid choice")
    