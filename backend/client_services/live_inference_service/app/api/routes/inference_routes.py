import asyncio
import base64
from fastapi import WebSocket
from app.api.main import app, redis
import logging
import numpy
import struct

NUM_CHANNELS = 16
FLOAT_LENGTH = 4
INFERENCE_PERIOD = 0.5
NUM_READINGS = 800

def data_to_numpy(data: list[bytes]):
    # print(data[0])
    return numpy.array([struct.unpack('16f', base64.b64decode(reading_set.encode('utf8'))) for reading_set in data])


@app.websocket("/inference/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    await websocket.accept()

    count = 0
    # ts = redis.ts()
    # await ts.create(f'ts-{session_id}')
    data_length = await redis.llen(str(session_id))
    while data_length < 1000:
        data_length = await redis.llen(str(session_id))

    # TODO load the model to make the inferences
    data = await redis.lrange(str(session_id), data_length-NUM_READINGS, -1)
    data = data_to_numpy(data)
    # data = data[-800:]
    while True:
        new_data = await redis.lrange(str(session_id), data_length, -1)
        new_length = len(new_data)
        new_data = data_to_numpy(new_data)
        if new_length > 0:
            data = numpy.vstack((data, new_data))
            data = data[-1*NUM_READINGS:]
            data_length = await redis.llen(str(session_id))
            await websocket.send_text(f"Sampled {new_length}")
            await asyncio.sleep(0.01)
