import asyncio
import json
from os import system
import websockets
import sys
import aioconsole # type: ignore
from datetime import datetime

uri = "ws://localhost:8765"

async def register(connection):
    clear_terminal()
    
    # Prompt username and check if it is unique
    username = await get_valid_username(connection)
    if username is None:  # User typed 'exit'
        await prompt_username(connection)
        return
        
    # Get valid password
    password = get_valid_password()
    
    # Register user
    success = await register_user(connection, username, password)
    
    # Handle result
    if success:
        print("\nRegistration successful!")
    else:
        print("\nSomething went wrong - please try again")
    
    input("Press any key to continue...")

async def get_valid_username(connection):
    # Get a username that doesn't already exist
    while True:
        username = input("Enter a username (or type 'exit' to quit): ")
        if username.lower() == 'exit':
            return None
            
        request_data = {
            "request_type": "check_username_exists",
            "username": username
        }
        await connection.send(json.dumps(request_data))
        response = json.loads(await connection.recv())
        
        if response["exists"] == "true":
            print("\nUsername already taken. Please try again.")
        else:
            return username

def get_valid_password():
    # Get a password that meets minimum requirements
    while True:
        password = input("Enter a password: ")
        if len(password) >= 3:
            return password
        print("Password must be at least 3 characters long. Please try again.")

async def register_user(connection, username, password):
    # Register the user with the server
    request_data = {
        "request_type": "register",
        "username": username,
        "password": password
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    return response["success"] == "true"

def print_in_color(text):
    # Print text in a given color
    print(f"\n\033[94m{text}\033[0m")
    



def clear_terminal():
       # Clear the terminal screen
    if sys.platform.startswith('win'):  # For Windows
        _ = system('cls')
    else:  # For Unix/Linux/MacOS
        _ = system('clear')
        
def display_message(message):
    # Parse ISO timestamp and format it to a more readable form
    timestamp = datetime.fromisoformat(message['timestamp']).strftime('%b/%d,%H:%M')  # e.g. "Nov 10, 21:45 
    print(f"{timestamp} {message['user_name']:<9} {message['content']}")

async def join_chatroom(connection, room_name, username, clear_screen=True):
    request_data = {
        "request_type": "join_room",
        "room": room_name
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    messages = response["messages"]
    if clear_screen:
        await start_chat(connection, messages, room_name, username)
    else:
        # Update chat display without clearing the screen
        for message in messages[-1:]:  # Display only the new message
            display_message(message)




async def receive_messages(connection, room_name, username):
    while True:
        try:
            response = await connection.recv()
            data = json.loads(response)
            if data.get("new_message") == room_name:
                # Re-fetch messages from the server
                await join_chatroom(connection, room_name, username, clear_screen=False)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

async def send_messages(connection, room_name, username):
    while True:
        # message = await aioconsole.ainput("\nEnter your message (or 'exit' to leave): ")
        message = await aioconsole.ainput("")
        # Move cursor up one line and clear it
        print('\033[F\033[K', end='')
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

async def start_chat(connection, messages, room_name, username):
    clear_terminal()
    print_in_color(f"\nChatting in {room_name}")
    
    for message in messages:
        display_message(message)
            
    # Start sending and receiving messages concurrently
    await asyncio.gather(
        receive_messages(connection, room_name, username),
        send_messages(connection, room_name, username)
    )
     


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


async def handle_join_chatroom(connection, chatrooms, username):
    clear_terminal()
    print_in_color("\nAvailable Chatrooms:")
    for i, room in enumerate(chatrooms):
        print(f"{i+1}. {room}")
                   
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
        input("Press any key to restart application")
        clear_terminal()
        await connection.close()
        await main()
        
    print_in_color(f"Logged in as {username}")
    
    # Get user choice
    print("What would you like to do?")
    print("    1. Join a chatroom")
    print("    2. Create new chatroom") 
    print("    3. Logout")
    choice = input("Enter your choice (1-3): ").lower()
    
    if choice == "1":
        await handle_join_chatroom(connection, response["chatrooms"], username)
    elif choice == "2":
         await create_new_chatroom(connection,username)
    elif choice == "3":
        print("You have logged out")
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

async def main():
    # Initialize the websocket connection
    connection = await init_websocket()
    await prompt_username(connection)
    
if __name__ == "__main__":
    asyncio.run(main())

