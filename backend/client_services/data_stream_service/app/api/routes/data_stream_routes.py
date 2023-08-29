import asyncio
from fastapi import WebSocket
from app.api.main import app, redis
import logging
import base64

NUM_CHANNELS = 16
FLOAT_LENGTH = 4

@app.websocket("/sample/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()
    count = 0
    # ts = redis.ts()
    # await ts.create(f'ts-{session_id}')

    while True:
        data: bytes = await websocket.receive_bytes()
        count += 1
        if count % 1000 == 0:
            with open('/test.txt', 'w') as file:
                file.write(str(count))
        # await ts.add(f'ts-{session_id}', "*", 3)
        commands = []
        for i in range(0, len(data), NUM_CHANNELS*FLOAT_LENGTH):
            subarray = data[i:i + NUM_CHANNELS*FLOAT_LENGTH]
            commands.append(redis.lpush(str(session_id), base64.b64encode(subarray).decode('utf8')))
        await asyncio.gather(*commands)
