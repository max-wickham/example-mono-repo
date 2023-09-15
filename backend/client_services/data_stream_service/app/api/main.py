# '''App entry point'''
# from fastapi import FastAPI
# from fastapi.responses import RedirectResponse
# from fastapi.openapi.docs import get_swagger_ui_html
# from starlette.middleware.cors import CORSMiddleware
# from redis.asyncio import from_url
# import redis

# from app.api.configs.configs import Config, environmentSettings
# from app.api.routes.udp_stream import udp_server

# redis = from_url(environmentSettings.REDIS_URL, decode_responses=True)

# app = FastAPI(
#     title=Config.application_name
# )

# origins = [
#     "http://localhost",
#     "https://dashboard-deploy-h3gpr.ondigitalocean.app",
#     "http://localhost:3000",
#     "*"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get('/')
# def docs():
#     '''Redirect to docs'''
#     return RedirectResponse('/docs')

# @app.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html(req):
#     root_path = req.scope.get("root_path", "").rstrip("/")
#     openapi_url = root_path + app.openapi_url
#     return get_swagger_ui_html(
#         openapi_url=openapi_url,
#         title="API",
#     )


# @app.on_event("startup")
# async def app_init():
#     '''App start up code'''
#     # Start up the udp server
#     loop = asyncio.get_event_loop()
#     asyncio.ensure_future(udp_server(), loop=loop)

# # import routes

# from app.api.routes.data_stream_routes import *


# from asyncio import sleep
# from sanic import Sanic

# app = Sanic("websocket")

# NUM_CHANNELS = 16
# FLOAT_LENGTH = 4


# @app.websocket("/sample")
# async def test(_, ws):
#     print('Connected')
#     count = 0
#     while True:
#         data = await ws.recv()
#         # print(data)
#         # Loop through the input_bytes and split into subarrays
#         sub_arrays = []
#         for i in range(0, len(data), NUM_CHANNELS*FLOAT_LENGTH):
#             subarray = data[i:i + NUM_CHANNELS*FLOAT_LENGTH]
#             sub_arrays.append(subarray)

#         for sub_array in sub_arrays:


#         count += 1
#         if count % 1000 == 0:
#             print(count)

# if __name__ == "__main__":
#     app.run(host="165.22.123.190", port=8005)




import asyncio
import base64

from redis.asyncio import from_url


MAX_BUFFER_LENGTH = 200000
PACKETS_SIZE = 48
REDIS_URL = 'redis://redis'

redis = from_url(REDIS_URL, decode_responses=True)



async def udp_server():
    # Create a UDP socket and bind it to a specific address and port
    transport, protocol = await asyncio.get_event_loop().create_datagram_endpoint(
        UdpServerProtocol,  # Protocol factory function
        local_addr=('0.0.0.0', 8888)  # Replace with your desired address and port
    )

    try:
        await asyncio.sleep(float('inf'))  # Keep the server running indefinitely
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()

class UdpServerProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        pass

    def connection_made(self, transport):
        print('connection')
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data
        assert data[0] == 0xAA
        session_id = int.from_bytes(data[1:5], byteorder='big', signed=False)
        raw_packets = data[5:]
        assert len(raw_packets) % PACKETS_SIZE == 0
        packets = []
        for i in range(0, len(raw_packets), PACKETS_SIZE):
            packet = raw_packets[i:i+PACKETS_SIZE]
            packet = base64.b64encode(packet).decode('utf8')
            packets.append(packet)
        asyncio.ensure_future(redis.rpush(str(session_id), *packets))
        async def check_data_length():
            current_length = await redis.llen(str(session_id))
            if current_length > MAX_BUFFER_LENGTH:
                await redis.ltrim(str(session_id), int(MAX_BUFFER_LENGTH / 10) , current_length)
        asyncio.ensure_future(check_data_length())


        print(f"Received data from {addr}: {len(message)}, {session_id}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(udp_server())
    loop.close()
