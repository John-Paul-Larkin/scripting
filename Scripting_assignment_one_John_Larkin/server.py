# John Paul Larkin
# c00001754
# 25/11/2024 - Scripting Assignment one

import asyncio
from os import system
import sys
import websockets
import sqlite3
import json
from datetime import datetime
import hashlib
from websockets.server import ServerProtocol
from websockets.exceptions import ConnectionClosed

PORT = 8765

DB_NAME = "./additional_files/chat.db"

# Dictionary to track users in each room: {room_name: set(websockets)}
room_connections: dict[str, set[ServerProtocol]] = {}

# Store active connections - This is used to broadcast messages to all clients
active_connections: set[ServerProtocol] = set()

# Helper function to clear the terminal screen
       # Clear the terminal screen
def clear_terminal():
    if sys.platform.startswith('win'):  # For Windows
        _ = system('cls')
    else:  # For Unix/Linux/MacOS
        _ = system('clear')

# Fetches a list of all chatrooms and sends to client
async def respond_with_list_of_chatrooms(websocket):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT room_name FROM messages")
    # Extract room names from tuples and remove duplicates
    chatrooms = cursor.fetchall()
    # fetchall returns a list of tuples
    # so convert to list of strings
    chatrooms = [room[0] for room in chatrooms] 
    # convert to set to remove duplicates
    chatrooms = list(set(chatrooms))
    chatrooms.sort()  # This will sort alphabetically in-place
    conn.close()
    
    response = {
        "success": "true",
        "chatrooms": chatrooms
    }
    await websocket.send(json.dumps(response))
    
# Handles new messages
async def new_message(request):
    # Extract message details - content, room, username, timestamp
    content = request["content"]
    room = request["room"]
    username = request["username"]
    timestamp = datetime.now().isoformat()
    
    # Store message in database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_name, timestamp, content, room_name) VALUES (?, ?, ?, ?)", (username, timestamp, content, room))
    conn.commit()
    conn.close()
    print('new_message sent')
    # Broadcast to all connections - Only the room the message was sent to will display it
    for connection in active_connections:
        await connection.send(json.dumps({"new_message": room}))
    

async def join_chatroom(request, websocket):
    room = request["room"]
    username = request["username"] 
    
    conn = sqlite3.connect(DB_NAME)
        
    # Add username to websocket object before adding to room
    websocket.username = username 
    
    # If this is the first time a user has joined this room, create a new set of connections for the room
    if room not in room_connections:
        room_connections[room] = set()
        
    # Add user to room
    room_connections[room].add(websocket)
    
    print(f"Adding {username} to room {room}")
    print(f"Room {room} now has {len(room_connections[room])} users")
    print(f"Current room_connections: {room_connections}")
    
    # Set row_factory to sqlite3.Row to access rows like dictionaries
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE room_name = ?", (room,))
 
    # Fetch all rows and convert to dictionaries
    messages = [dict(row) for row in cursor.fetchall()]
    
     # Get current users in room
    active_users = []
    # Loop through all connections in the room
    for conn in room_connections[room]:
        # If the connection has a username, add it to the list
        # This is set in handle_client
        if hasattr(conn, 'username'):  
            active_users.append(conn.username)     
    print(f"Active users in room {room}: {active_users}")
            
    conn.close()
    response = {
        "success": "true", 
        "messages": messages,
        "active_users": active_users
    }
    # Return messages and active users to the client
    await websocket.send(json.dumps(response))
    
async def login(request,websocket):
    username = request["username"]
    password = request["password"]
    
    # Hash the provided password using SHA-256 before comparing to hashed password in database
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Check credentials
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Fetch the hashed password for the username
    cursor.execute("SELECT password FROM users WHERE user_name = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    # If the password matches the hashed password in the database, login is successful
    if result and result[0] == hashed_password:
        response = {"success": "true"}
    else:
        response = {"success": "false", "error": "Invalid credentials"}
    
    await websocket.send(json.dumps(response))

# Checks if a username already exists in the database   
async def check_username_exists(request,websocket):
    username = request["username"]
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Fetch the user with the username
    cursor.execute("SELECT * FROM users WHERE user_name = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    # Return true if the username exists, false otherwise
    await websocket.send(json.dumps({"exists": "true" if exists else "false"}))

# Registers a new user
async def register(request,websocket):
    username = request["username"]
    password = request["password"]
    
    # Hash the password using SHA-256 before adding to database
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Store user in database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        # Insert the username and hashed password into the database
        cursor.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", 
                      (username, hashed_password))
        conn.commit()
        response = {"success": "true"}
    except sqlite3.Error as e:
        response = {"success": "false", "error": str(e)}
    finally:
        conn.close()
    
    await websocket.send(json.dumps(response))

# Creates a new chatroom
async def create_new_chatroom(request,websocket):
    room_name = request["room_name"]
    username = request["user_name"] 
    # Get current timestamp
    timestamp = datetime.now().isoformat()
    
    conn = sqlite3.connect(DB_NAME)  
    cursor = conn.cursor()
    # Select all rows where the room name matches the room name requested
    cursor.execute("SELECT room_name FROM messages WHERE room_name = ?", (room_name,))
     # Check if room already exists
    exists = cursor.fetchone() is not None
    
    if exists:
        # If room already exists, return false and an error message
        await websocket.send(json.dumps({"success": "false", "error": "Room already exists"}))
    else:
        # If room does not exist, insert the room name, username, timestamp and welcome message into the database
        cursor.execute("INSERT INTO messages (user_name, timestamp, content, room_name) VALUES (?, ?, ?, ?)", (username, timestamp, "Welcome to the chat!", room_name))
        conn.commit()
        # Return true to indicate success
        await websocket.send(json.dumps({"success": "true"}))
    conn.close()
    
    
# Handles all requests from clients
# This is the main function that runs when a client connects

async def handle_client(websocket):
    print("New client connected!") 
    try:
        # When a client connects, add to set
        active_connections.add(websocket)
        user_rooms = set() 
        print(f"Active connections: {len(active_connections)}")
        
        # Start a ping task - This is used to keep the connection alive 
        # When the user is not in a room, the ping will keep the connection alive
        ping_task = asyncio.create_task(keep_alive(websocket))
        
        async for request in websocket:
            request = json.loads(request)
            request_type = request["request_type"]
            
            if request_type == "get_chatrooms":
                await respond_with_list_of_chatrooms(websocket)
            elif request_type == "create_room":
                await create_new_chatroom(request,websocket)
            elif request_type == "join_room":
                # Add room to user's set of rooms
                # This is used to track which rooms have actuve users
                room = request["room"]
                user_rooms.add(room)
                # Add username to websocket object before adding to room
                websocket.username = request["username"]  
                await join_chatroom(request, websocket)
            elif request_type == "login":
                await login(request,websocket)
            elif request_type == "new_message":
                await new_message(request)
            elif request_type == "check_username_exists":
                await check_username_exists(request,websocket)
            elif request_type == "register":
                await register(request,websocket)
            else:
                print("Invalid request type")
        
    except ConnectionClosed:
        print("Client disconnected normally")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Clean up
        ping_task.cancel()  # Cancel the ping task
        for room in user_rooms:
            # For every room in user_rooms
            if room in room_connections:
                # Remove this user from the room
                room_connections[room].remove(websocket)
                # Notify others that user left
                if hasattr(websocket, 'username'):
                    leave_notification = {
                        "type": "user_left",
                        "username": websocket.username,
                        "room": room
                    }
                    for conn in room_connections[room]:
                        try:
                            await conn.send(json.dumps(leave_notification))
                        except:
                            pass
        active_connections.remove(websocket)

# Add this new function to handle keepalive pings
async def keep_alive(websocket):
    try:
        while True:
            try:
                await websocket.ping()
                # Send ping every 20 seconds
                await asyncio.sleep(20)  
            except:
                break
    except:
        pass

# Starts the WebSocket server
async def start_server():
    server = await websockets.serve(handle_client, "localhost", PORT)
    print(f"WebSocket server started on ws://localhost:{PORT}")
    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("WebSocket server stopped")