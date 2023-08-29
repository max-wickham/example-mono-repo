import asyncio
import websockets

async def hello():
    uri = "ws://165.22.123.190:8005/sample"
    async with websockets.connect(uri) as websocket:
        while True:
            await websocket.send("Hi")

asyncio.get_event_loop().run_until_complete(hello())
