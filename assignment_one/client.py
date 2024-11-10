import asyncio
import json
from os import system
import websockets
import sys

uri = "ws://localhost:8765"


async def register(connection):
    clear_terminal()
    while True:
        username = input("Enter a username (or type 'exit' to quit): ")
        if username.lower() == 'exit':
            await prompt_username(connection)
            break
        else:
            request_data = {
                "request_type": "check_username_exists",
                "username": username
            }
            await connection.send(json.dumps(request_data))
            response = json.loads(await connection.recv())
            
            if response["exists"] == "true":
                print("\nUsername already taken. Please try again.")
            else:
                break
            
    while True:
        password = input("Enter a password: ")
        if len(password) >= 3:
            break 
        print("Password must be at least 3 characters long. Please try again.")
    
    
    
    request_data = {
        "request_type": "register",
        "username": username,
        "password": password
    }
        
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
        
    if response["success"] == "true":
        print("\nRegistration successful!")
        input("Press any key to continue...")
        return
    else:
        print("\nSomething went wrong - please try again")
        input("Press any key to continue...")

def display_list_of_chatrooms(chatrooms):
    clear_terminal()
    print("\n\033[94mAvailable Chatrooms:\033[0m")
    for i, room in enumerate(chatrooms):
        print(f"{i+1}. {room}")

def clear_terminal():
       # Clear the terminal screen
    if sys.platform.startswith('win'):  # For Windows
        _ = system('cls')
    else:  # For Unix/Linux/MacOS
        _ = system('clear')
        
async def join_chatroom(connection, room_name, username):
    request_data = {
        "request_type": "join_room",
        "room": room_name
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    messages = response["messages"]
    await start_chat(connection, messages, room_name, username)
    
        
async def start_chat(connection, messages, room_name, username):  
    clear_terminal()
    print(f"\n\033[94mChatting in {room_name}\033[0m")
    
    for message in messages:    
        timestamp = message['timestamp'].split('.')[0]  # Remove microseconds for cleaner display
        # Format the username to be left-aligned with a width of 12 characters
        print(f"[{timestamp}] {message['user_name']:<9} {message['content']}")
        
    while True:
        message = input("\nEnter your message (or 'exit' to leave): ")
        
        if message.lower() == 'exit':
            await logged_in(connection, username)
            break
            
        request_data = {
            "request_type": "new_message",
            "content": message,
            "room": room_name,
            "username": username
        }
        await connection.send(json.dumps(request_data))

     
async def init_websocket():
    try:
        connection = await websockets.connect(uri)
        print(f"Connected to {uri}")
        return connection
    except websockets.exceptions.ConnectionError:
        print(f"Could not connect to {uri}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def create_new_chatroom(connection, username):
    room_name = input("Enter a name for the new chatroom: ")
    request_data = {
        "request_type": "create_room",
        "room_name": room_name,
        "user_name": username
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    if response["success"] == "true":
        print(f"Chatroom '{room_name}' created successfully!")
        input("Press any key to continue...")
        await start_chat(connection, [], room_name, username)
    elif response["success"] == "false":
        print(f"Failed to create chatroom: {response['error']}")
        input("Press any key to continue...")
        
async def logged_in(connection,username):
    clear_terminal()
    # Get list of chatrooms from server
    request_data = {
        "request_type": "get_chatrooms"
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    
    if response["success"] == "false":
        print("Failed to get chatrooms")
        print("restarting application")
        await connection.close()
        await main()
             
    # Get user choice
    print("What would you like to do?")
    print("    1. Join a chatroom")
    print("    2. Create new chatroom") 
    print("    3. Logout")
    choice = input("Enter your choice (1-3): ").lower()
    
    if choice == "1":
        chatrooms = response["chatrooms"]
        clear_terminal()
        display_list_of_chatrooms(chatrooms)             
        room_choice = input("Enter the number of the chatroom you'd like to join: ").lower()
        try:
            if room_choice == "exit":
                await prompt_username(connection)
                return
            room_index = int(room_choice) - 1
            if 0 <= room_index < len(chatrooms):
                await join_chatroom(connection, chatrooms[room_index],username)
            else:
                print("Invalid room number")
                await logged_in(connection,username)
        except ValueError:
            print("Please enter a valid number")
            await logged_in(connection,username)
    elif choice == "2":
         await create_new_chatroom(connection,username)
    elif choice == "3":
        print("You have been logged out")
        input("Press any key to continue...")
        await prompt_username(connection)
    elif choice == "exit":
        print("Exiting...")
        input("Press any key to continue...")
        await connection.close()
        main()
    else:
        print("Invalid choice")
        await logged_in(connection,username)

async def login(connection):
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    login_data = {
        "request_type": "login",
        "username": username,
        "password": password
    }
    
    await connection.send(json.dumps(login_data))
    response = json.loads(await connection.recv())
    
    if response["success"] == "true":
        await logged_in(connection, username)
    else:
        print("Login failed - check username and password")
        input("Press any key to continue...")
        await prompt_username(connection)

async def prompt_username(connection):
    if connection:
        while True:    
            clear_terminal()
            print("Welcome! Please choose an option:")
            print("    1. Login")
            print("    2. Register") 
            print("    3. Exit")
            choice = input("Enter your choice (1-3): ").lower()
            
            if choice == "1" or choice == "login":
                await login(connection)
            elif choice == "2" or choice == "register":
                await register(connection)
            elif choice == "3" or choice == "exit":
                await connection.close()
                print("Exiting...")
                return
            else:
                print("Invalid choice. Enter (1-3)")
                input("Press any key to continue...")
                


async def main():
    # Initialize the websocket connection
    connection = await init_websocket()
    await prompt_username(connection)
    

if __name__ == "__main__":
    asyncio.run(main())
    # except KeyboardInterrupt:
    #     print("\nClosing connection...")
    #     sys.exit(0)
