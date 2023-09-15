import asyncio
import base64

from fastapi import WebSocket,Request

from app.api.main import app, redis

# NUM_CHANNELS = 16
# FLOAT_LENGTH = 3
PACKET_SIZE_BYTES = 33

@app.websocket("/sample/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()
    print('client connected', session_id)
    # ts = redis.ts()
    # await ts.create(f'ts-{session_id}')

    while True:
        data: bytes = await websocket.receive_bytes()
        print('received bytes', len(data))
        with open('/test.txt','w') as file:
            file.write(f'received {len(data)}')
        # await ts.add(f'ts-{session_id}', "*", 3)
        commands = []
        for i in range(0, len(data), PACKET_SIZE_BYTES):
            subarray = data[i:i + PACKET_SIZE_BYTES]
            commands.append(redis.lpush(str(session_id), base64.b64encode(subarray).decode('utf8')))
        await asyncio.gather(*commands)


@app.post("/sample/{session_id}")
async def http_endpoint(request: Request, session_id: int):
    # ts = redis.ts()
    # await ts.create(f'ts-{session_id}')
    # print(f'stream {session_id}')
    data: bytes = await request.body()
    print(len(data))
    commands = []
    subarrays = []
    for i in range(0, len(data), PACKET_SIZE_BYTES):
        subarray = data[i:i + PACKET_SIZE_BYTES]
        subarrays.append(base64.b64encode(subarray).decode('utf8'))
    await redis.rpush(str(session_id), *subarrays)
    # await asyncio.gather(*commands)
