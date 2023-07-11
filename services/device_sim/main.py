'''Stream fake device data'''

import websockets
import asyncio
import time

from schemas.bin_messages.compiled_messages.sensor_data_pb2 import SensorReadingPacket

from configs.configs import EnvironmentSettings



# send binary data of the correct format

device_id = 'asdf'

time.sleep(5)

async def send_fake_data():
    print(f'{EnvironmentSettings.SOCKET_URL}/{device_id}')
    async with websockets.connect(f'{EnvironmentSettings.SOCKET_URL}/{device_id}') as websocket:


        data: bytes = SensorReadingPacket(
            time_s=time.time(),
            data = [0] * 16
        ).SerializeToString()
        await websocket.send(data)
        # response = await websocket.recv()

asyncio.get_event_loop().run_until_complete(send_fake_data())
