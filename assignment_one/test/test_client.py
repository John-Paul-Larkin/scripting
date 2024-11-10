import asyncio
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

async def connect_websocket():
    try:
        connection = await init_websocket()
        if not connection:
            return None
            
        while True:
            message = input("Enter message (or 'quit' to exit): ")
            
            if message.lower() == 'quit':
                break
            
            await connection.send(message)
            print(f"Sent: {message}")
            
            response = await connection.recv()
            print(f"Received: {response}")
            
        return connection
            
    finally:
        if connection:
            await connection.close()

async def send_message(websocket, message):
    if websocket:
        await websocket.send(message)
        response = await websocket.recv()
        return response
    return None

async def main():
    # Initialize the websocket connection
    connection = await init_websocket()
    if connection:
        response = await send_message(connection, "Hello Server!")
        print(f"Test message response: {response}")
        
        # Start the main message loop
        await connect_websocket()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClosing connection...")
        sys.exit(0)
