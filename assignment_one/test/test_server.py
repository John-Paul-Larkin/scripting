import asyncio
import websockets

async def handle_client(websocket):
    try:
        async for message in websocket:
            print(f"Received: {message}")
            # Echo the message back to the client
            await websocket.send(f"Server received: {message}")
            print(f"Sent: Server received: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def start_server():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed() 

def main():
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("WebSocket server stopped")

if __name__ == "__main__":
    main()
