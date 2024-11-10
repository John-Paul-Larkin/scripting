import asyncio
import websockets
import sqlite3
import json
from datetime import datetime

PORT = 8765

async def handle_client(websocket):
    try:
        async for request in websocket:
            request = json.loads(request)
            
            request_type = request["request_type"]
            
            if request_type == "get_chatrooms":
                # TODO: Implement fetching chatrooms from database
                chatrooms = ["General", "Random", "Tech"]  # Placeholder
                response = {
                    "success": "true",
                    "chatrooms": str(chatrooms)
                }
                await websocket.send(json.dumps(response))
                continue

            elif request_type == "join_room":
                room = request["room"]
                # TODO: Implement fetching room messages from database
                messages = []  # Placeholder for room messages
                response = {
                    "success": "true", 
                    "messages": messages
                }
                await websocket.send(json.dumps(response))
                continue

            elif request_type == "login":
                username = request["username"]
                password = request["password"]
                # TODO: Implement password verification
                # For now, accept any login
                response = {
                    "success": "true"
                }
                await websocket.send(json.dumps(response))
                continue
            
            
            
            
            
            
            
            
            
            
            
            response = {
                "success": "true",
                "response": "message received"
            }   
            await websocket.send(json.dumps(response))
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