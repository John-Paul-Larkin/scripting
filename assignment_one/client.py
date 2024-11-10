
import asyncio
import json
import websockets
import sys

uri = "ws://localhost:8765"

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

async def logged_in(connection):
    # Get list of chatrooms from server
    request_data = {
        "request_type": "get_chatrooms"
    }
    await connection.send(json.dumps(request_data))
    response = json.loads(await connection.recv())
    
    if response.success == "false":
        print("Failed to get chatrooms")
        print("restarting application")
        await connection.close()
        await main()
    else:
        # Display chatrooms
        print("\nAvailable Chatrooms:")
        for i, room in enumerate(eval(response["chatrooms"])):
            print(f"{i+1}. {room}")
        chatrooms = response["chatrooms"]
        # Get user choice
    print("\nWhat would you like to do?")
    print("1. Join a chatroom")
    print("2. Create new chatroom") 
    print("3. Logout")
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        room_choice = input("Enter the number of the chatroom you'd like to join: ")
        try:
            room_index = int(room_choice) - 1
            if 0 <= room_index < len(eval(chatrooms)):
                request_data = {
                    "request_type": "join_room",
                    "room": eval(chatrooms)[room_index]
                }
                await connection.send(json.dumps(request_data))
                messages = json.loads(await connection.recv())
                # await start_chat(connection, messages)
            else:
                print("Invalid room number")
                await logged_in(connection)
        except ValueError:
            print("Please enter a valid number")
            await logged_in(connection)
            
    elif choice == "2":
        # await make_new_chatroom(connection)
        print("make new chatroom not implemented yet")
        
    elif choice == "3":
        await prompt_username(connection)
        
    else:
        print("Invalid choice")
        await logged_in(connection)



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
    
    if response.success == "true":
        await logged_in(connection)
    else:
        print("Login failed - check username and password")
        await prompt_username(connection)

async def prompt_username(connection):
    if connection:
        while True:
            print("\nWelcome! Please choose an option:")
            print("1. Login")
            print("2. Register") 
            print("3. Exit")
            choice = input("Enter your choice (1-3): ")
            
            if choice == "1":
                await login(connection)
            elif choice == "2":
                # await register(connection)
                print("Register not implemented yet")
            elif choice == "3":
                await connection.close()
                print("Exiting...")
                return
            else:
                print("Invalid choice. Enter (1-3)")


async def main():
    # Initialize the websocket connection
    connection = await init_websocket()
    await prompt_username(connection)
    





if __name__ == "__main__":
    asyncio.run(main())
    # except KeyboardInterrupt:
    #     print("\nClosing connection...")
    #     sys.exit(0)
