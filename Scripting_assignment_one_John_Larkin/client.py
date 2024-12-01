
# John Paul Larkin
# c00001754
# 25/11/2024 - Scripting Assignment one
import asyncio
import json
from os import system
import websockets
import sys
import aioconsole # type: ignore
from datetime import datetime

# Note: Please read functions from bottom up to understand the flow of the program

# Send data to server and handle connection loss
# If connection is lost, attempt to reconnect and send data to new connection
async def safe_send(connection, data):
    try:
        await connection.send(json.dumps(data))
    except websockets.exceptions.ConnectionClosedError:
        # If connection is lost, attempt to reconnect
        print("\nConnection lost. Attempting to reconnect...")
        new_connection = await init_websocket()
        if new_connection:
            # Send data to new connection
            await new_connection.send(json.dumps(data))
            return new_connection
        else:
            # If reconnection fails, inform the user and exit
            print("Could not reconnect. Please restart the application.")
            sys.exit(1)
    return connection

# Receive data from server and handle connection loss
async def safe_receive(connection):
    try:
        # Return data from server
        return await connection.recv()
    except websockets.exceptions.ConnectionClosedError:
        # If connection is lost, attempt to reconnect
        print("\nConnection lost. Attempting to reconnect...")
        new_connection = await init_websocket()
        if new_connection:
            # Return data from new connection
            return await new_connection.recv()
        else:
            print("Could not reconnect. Please restart the application.")
            sys.exit(1)


# Get a username that doesn't already exists
async def get_valid_username(connection):
    # Prompt user for username until they type 'exit' or a unique username is entered
    while True:
        username = input("Enter a username (or type 'exit' to quit): ")
        if username.lower() == 'exit':
            return None
            
        request_data = {
            "request_type": "check_username_exists",
            "username": username
        }
        # Send request to server to check if username exists
        await connection.send(json.dumps(request_data))
        response = json.loads(await connection.recv())
        
        if response["exists"] == "true":
            # If username is already taken, inform the user and loop to prompt for a new username
            print("\nUsername already taken. Please try again.")
        else:
            return username

# Get a password that meets minimum requirements
def get_valid_password():
    # Get a password that meets minimum requirements
    # To keep it simple, check it is at least 3 characters long
    while True:
        password = input("Enter a password: ")
        if len(password) >= 3:
            return password
        print("Password must be at least 3 characters long. Please try again.")

# Register a new user
async def register(connection):
    clear_terminal()
    
    # Prompt username and check if it is unique
    username = await get_valid_username(connection)
    # User typed 'exit'
    if username is None:  
        await display_initial_menu(connection)
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

# Register a new user with the server
async def register_user(connection, username, password):
    request_data = {
        "request_type": "register",
        "username": username,
        "password": password
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    # Return true if registration is successful, false otherwise
    return response["success"] == "true"

# Helper function to print text in a given color
def print_in_color(text):
    print(f"\n\033[94m{text}\033[0m")
    
# Helper function to clear the terminal screen
def clear_terminal():
       # Clear the terminal screen
    if sys.platform.startswith('win'):  # For Windows
        _ = system('cls')
    else:  # For Unix/Linux/MacOS
        _ = system('clear')
        
def display_individual_message(message):
    # Parse ISO timestamp and format it to a more readable form
    timestamp = datetime.fromisoformat(message['timestamp']).strftime('%b/%d,%H:%M')  # e.g. Nov 10, 21:45 
    print(f"{timestamp} {message['user_name']:<9} {message['content']}")

# Request all messages from server for a specific chatroom and display them
async def join_chatroom(connection, room_name, username, clear_screen=True):
    request_data = {
        "request_type": "join_room",
        "room": room_name,
        "username": username
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    messages = response["messages"]
    # Get list of connected users
    active_users = response.get("active_users")  
    
    if clear_screen:
        await start_chat(connection, messages, room_name, username, active_users)
    else:
        # Update chat display without clearing the screen
        for message in messages[-1:]:
            display_individual_message(message)

# async wait for new messages from server and handle them
async def receive_messages(connection, room_name, username):
    while True:
        try:
            response = await connection.recv()
            data = json.loads(response)
            # If the server has a new message for this chatroom,
            if data.get("new_message") == room_name:
                # Re-fetch all messages from the server and display them
                await join_chatroom(connection, room_name, username, clear_screen=False)
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# async wait for user to input a message and send to server
async def send_messages(connection, room_name, username):
    while True:
       #  read user input asynchronously without blocking the event loop
        message = await aioconsole.ainput("")
        # Move cursor up one line and clear it - ie remove the message the user just sent
        print('\033[F\033[K', end='')
        if message.lower() == 'exit':
            # User can type 'exit' to return to the main menu at any times
            await prompt_login(connection)
            break
        # Else send message to server
        request_data = {
            "request_type": "new_message",
            "content": message,
            "room": room_name,
            "username": username
        }     
        await connection.send(json.dumps(request_data))

# Start the chat - display existing messages and start sending and receiving messages concurrently
async def start_chat(connection, messages, room_name, username, active_users):
    clear_terminal()
    print_in_color(f"\nChatting in {room_name}")
    print_in_color(f"Connected users ({len(active_users)}): {', '.join(active_users)}")
    
    # Display existing messages - in reverse chronological orde
    # Note messages may be empty if its a new chatroom
    for message in messages:
        # Display each message - with timestamp, username and content
        display_individual_message(message)
            
    # Start sending and receiving messages concurrently
    await asyncio.gather(
        receive_messages(connection, room_name, username),
        send_messages(connection, room_name, username)
    )
    
# Prompt user for a name for the new chatroom and send to server to create it
async def create_new_chatroom(connection, username):
    room_name = input("Enter a name for the new chatroom: ")
    request_data = {
        "request_type": "create_room",
        "room_name": room_name,
        "user_name": username
    }
    # Send request to server to create new chatroom
    await connection.send(json.dumps(request_data))
    # Receive response from server and parse json
    response = json.loads(await connection.recv())
    if response["success"] == "true":
        # If chatroom creation is successful, inform the user and start the chat
        print(f"Chatroom '{room_name}' created successfully!")
        input("Press any key to continue...")
        # Start the chat - pass an empty list of messages, since this is a new chatroom, there are no existing messages
        await start_chat(connection, [], room_name, username, [username])
    elif response["success"] == "false":
        # If chatroom creation fails, inform the user and return to the logged in menu
        print(f"Failed to create chatroom: {response['error']}")
        input("Press any key to continue...")  
        await display_logged_in_menu(connection,username)
         
# Get list of chatrooms from server, display them to the user and handle their choice
async def handle_join_chatroom(connection, username):
    # Clear terminal screen
    clear_terminal()
    # Get list of chatrooms from server
    request_data = {
        "request_type": "get_chatrooms"
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    chatrooms = response["chatrooms"]
    
    # If the server failed to get chatrooms, inform the user and restart application
    if response["success"] == "false":
        print("Failed to get chatrooms")
        input("Press any key to restart application")
        clear_terminal()
        await connection.close()
        await main()

    print_in_color("\nAvailable Chatrooms:")
    # Display chatrooms to the user, with an index for selection
    # Note: Index starts at 1, not 0
    for i, room in enumerate(chatrooms):
        print(f"{i+1}. {room}")
                   
    room_choice = input("Enter the number of the chatroom you'd like to join: ").lower()
    try:
        # The user can type 'exit' to return to the main menu
        if room_choice == "exit":
            await display_initial_menu(connection)
            return
        # Convert user choice to an index by subtracting 1 
        room_index = int(room_choice) - 1
        if 0 <= room_index < len(chatrooms):
            # If the room index is valid, join the chatroom
            await join_chatroom(connection, chatrooms[room_index],username)
        else:
            # If the room index is outside the range of the list, inform the user and return to the logged in menu
            print("Invalid room number")
        await display_logged_in_menu(connection,username)
    except ValueError:
        # If the user did not enter a valid input, inform them and return to the logged in menu
        print("Please enter a valid number")
        await display_logged_in_menu(connection,username)
        
# Display options for logged in user and handle their choice
async def display_logged_in_menu(connection,username):
    clear_terminal()
    print_in_color(f"Logged in as {username}")
    # Get user choice
    print("What would you like to do?")
    print("    1. Join a chatroom")
    print("    2. Create new chatroom") 
    print("    3. Logout")
    choice = input("Enter your choice (1-3): ").lower()

    if choice == "1" or choice == "join":
        await handle_join_chatroom(connection, username)
    elif choice == "2" or choice == "create":
         await create_new_chatroom(connection,username)
    elif choice == "3" or choice == "logout":
        # Reutrn to the main menu
        print("You have logged out")
        input("Press any key to continue...")
        await display_initial_menu(connection)
    elif choice == "exit":
        # Close connection and restart application
        print("Exiting...")
        input("Press any key to continue...")
        await connection.close()
        main()
    else:
        
        print("Invalid choice")
        await display_logged_in_menu(connection,username)

# Prompt user for username and password and send to server to check if login is successful
async def prompt_login(connection):
    username = input("Enter username: ")
    password = input("Enter password: ")
    login_data = {
        "request_type": "login",
        "username": username,
        "password": password
    }
    
    try:
        # Use safe send/receive
        connection = await safe_send(connection, login_data)
        response = json.loads(await safe_receive(connection))
        
        if response["success"] == "true":
            # If login is successful, display logged in menu
            await display_logged_in_menu(connection, username)
        else:
            # If login fails, inform the user and display initial menu again
            print("Login failed - check username and password")
            input("Press any key to continue...")
            await display_initial_menu(connection)
    except Exception as e:
        print(f"Error during login: {e}")
        input("Press any key to continue...")
        await display_initial_menu(connection)

 
             
# Display login options and handle users input
async def display_initial_menu(connection):
    if connection:
        # Keep displaying login options until user chooses to exit
        while True:    
            clear_terminal()
            print("Welcome! Please choose an option:")
            print("    1. Login")
            print("    2. Register") 
            print("    3. Exit")
            choice = input("Enter your choice (1-3): ").lower()
            
            if choice == "1" or choice == "login":
                await prompt_login(connection)
            elif choice == "2" or choice == "register":
                await register(connection)
            elif choice == "3" or choice == "exit":
                await connection.close()
                print("Exiting...")
                return
            else:
                print("Invalid choice. Enter (1-3)")
                input("Press any key to continue...")


# Initialise and return the websocket connection
async def init_websocket():
    # TCP port 8765 is hardcoded
    uri = "ws://localhost:8765" 
    max_retries = 5
    retry_count = 0
    
    # Try to connect to the server up to 5 times
    while retry_count < max_retries:
        try:
            connection = await websockets.connect(
                uri,
                ping_interval=20,
                ping_timeout=60,
            )
            print(f"Connected to {uri}")
            return connection
        # If connection fails with a WebSocketException, ConnectionRefusedError, or OSError, print error and retry up to 5 times
        except (websockets.exceptions.WebSocketException, 
                ConnectionRefusedError, 
                OSError) as e:
            print(f"Could not connect to {uri}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying... ({retry_count}/{max_retries})")
                await asyncio.sleep(1)
            else:
                print("Failed to connect after multiple attempts")
                return None
    return None

async def main():
    while True:  # Add retry loop
        try:
             # Initialize websocket connection
            connection = await init_websocket()
            if connection is None:
                print("Could not establish connection to server. Please make sure the server is running.")
                return
            
            # Display login menu/options
            await display_initial_menu(connection)
            break  # Exit loop if everything completes normally
            
        except websockets.exceptions.ConnectionClosedError:
            print("\nConnection lost. Attempting to reconnect...")
            await asyncio.sleep(1)  # Wait before retrying
            continue
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main())

