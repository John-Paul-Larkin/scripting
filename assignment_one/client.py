
import socket


def login(username, password):
    print("Logging in...")


def register(username, password):
    print("Registering...")

PORT  = 8080

def tcp_client():
    # create the socket object
    client_socket = socket.socket(socket.AF_INET, 
                                socket.SOCK_STREAM )
    
    client_socket.connect(('localhost',PORT))
    
    client_socket.send("Hello Server!!!!".encode())
    response = client_socket.recv(1024).decode()
    print(f"Received from the server: {response}")
    client_socket.close()   

if __name__ == "__main__":
    print("Welcome to the chat app.")
    print("Do you want to login or register?")
    print("   1. Login")
    print("   2. Register")
    # choice = input("Enter your choice: ")
    
    # if choice == "1":
    #     username = input("Enter your username: ")
    #     password = input("Enter your password: ")
    #     login(username, password)
    # elif choice == "2":
    #     username = input("Enter your username: ")
    #     password = input("Enter your password: ")
    #     register(username, password)
    
    tcp_client()