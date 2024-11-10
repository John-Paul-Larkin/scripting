import asyncio
import websockets
import sqlite3
import json
from datetime import datetime
import hashlib

PORT = 8765

DB_NAME = "chat.db"

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
    
    
async def new_message(request,websocket):
    content = request["content"]
    room = request["room"]
    username = request["username"]
    timestamp = datetime.now().isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_name, timestamp, content, room_name) VALUES (?, ?, ?, ?)", (username, timestamp, content, room))
    conn.commit()
    conn.close()
    print('new_message sent')
    await websocket.send(json.dumps({"new_message": room}))
    

async def join_chatroom(request,websocket):
    room = request["room"]
    conn = sqlite3.connect(DB_NAME)
    
    # Method 1: Set row_factory to sqlite3.Row
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE room_name = ?", (room,))
    # Now you can access rows like dictionaries
    messages = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    response = {
        "success": "true", 
        "messages": messages
    }
    await websocket.send(json.dumps(response))
    
async def login(request,websocket):
    username = request["username"]
    password = request["password"]
    
    # Hash the provided password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Check credentials
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE user_name = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == hashed_password:
        response = {"success": "true"}
    else:
        response = {"success": "false", "error": "Invalid credentials"}
    
    await websocket.send(json.dumps(response))

async def check_username_exists(request,websocket):
    username = request["username"]
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_name = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    await websocket.send(json.dumps({"exists": "true" if exists else "false"}))

async def register(request,websocket):
    username = request["username"]
    password = request["password"]
    
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Store user in database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", 
                      (username, hashed_password))
        conn.commit()
        response = {"success": "true"}
    except sqlite3.Error as e:
        response = {"success": "false", "error": str(e)}
    finally:
        conn.close()
    
    await websocket.send(json.dumps(response))

async def create_new_chatroom(request,websocket):
    room_name = request["room_name"]
    username = request["user_name"]
    timestamp = datetime.now().isoformat()
    conn = sqlite3.connect(DB_NAME)  
    cursor = conn.cursor()
    
    # Check if room already exists
    cursor.execute("SELECT room_name FROM messages WHERE room_name = ?", (room_name,))
    exists = cursor.fetchone() is not None
    
    if exists:
        await websocket.send(json.dumps({"success": "false", "error": "Room already exists"}))
    else:
        cursor.execute("INSERT INTO messages (user_name, timestamp, content, room_name) VALUES (?, ?, ?, ?)", (username, timestamp, "Welcome to the chat!", room_name))
        conn.commit()
        await websocket.send(json.dumps({"success": "true"}))
    conn.close()
    
    

async def handle_client(websocket):
    try:
        async for request in websocket:
            request = json.loads(request)
            request_type = request["request_type"]
            
            if request_type == "get_chatrooms":
                await respond_with_list_of_chatrooms(websocket)
            elif request_type == "create_room":
                await create_new_chatroom(request,websocket)
            elif request_type == "join_room":
                await join_chatroom(request,websocket)
            elif request_type == "login":
                await login(request,websocket)
            elif request_type == "new_message":
                await new_message(request,websocket)
            elif request_type == "check_username_exists":
                await check_username_exists(request,websocket)
            elif request_type == "register":
                await register(request,websocket)
            else:
                print("Invalid request type")
        
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def start_server():
    server = await websockets.serve(handle_client, "localhost", PORT)
    print(f"WebSocket server started on ws://localhost:{PORT}")
    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("WebSocket server stopped")