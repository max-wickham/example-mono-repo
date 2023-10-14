import asyncio
import websockets



email = "mtt.pzz56@gmail.com"
password = "test"
session_id = 201326592
model_id = "652abd481936058633ca293f"
async def connect_to_websocket_server():
    uri = f"ws://138.68.161.150:8006/inference/{session_id}/{model_id}/{email}/{password}"  # Replace with the actual WebSocket server URL

    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")

asyncio.get_event_loop().run_until_complete(connect_to_websocket_server())
