'''Run a UDP server to receive incoming device streams and add to redis'''
import sys; sys.path.insert(0,'/')
import os
import asyncio
import base64

from redis.asyncio import from_url

from configs.commons import StreamingConfigs

MAX_BUFFER_LENGTH = StreamingConfigs.MAX_BUFFER_LENGTH
BYTES_PER_INT = StreamingConfigs.BYTES_PER_INT

REDIS_URL = os.environ['REDIS_URL']
redis = from_url(REDIS_URL, decode_responses=True)



async def udp_server():
    '''Run the udp server'''
    # Create a UDP socket and bind it to a specific address and port
    transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
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
    '''Controller for UDP server'''

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        '''
        Receive data from the device and insert into redis
        The encoding of the bits received are as follows
        0:1 = 0xAA
        1:5 = session id
        5:6 = num channels
        6:8 = frequency hz
        '''
        assert data[0] == 0xAA
        session_id = int.from_bytes(data[1:5], byteorder='big', signed=False)
        num_channels = int.from_bytes(data[5:6], byteorder='big', signed=False)
        frequency_hz = int.from_bytes(data[6:8], byteorder='big', signed=False)
        packet_size = num_channels * BYTES_PER_INT
        asyncio.ensure_future(redis.set(f'{session_id}_CHANNEL_COUNT', num_channels))
        asyncio.ensure_future(redis.set(f'{session_id}_FREQUENCY_HZ', frequency_hz))

        raw_packets = data[8:]
        assert len(raw_packets) % packet_size == 0
        packets = []
        for i in range(0, len(raw_packets), packet_size):
            packet = raw_packets[i:i+packet_size]
            packet = base64.b64encode(packet).decode('utf8')
            packets.append(packet)
        asyncio.ensure_future(redis.rpush(str(session_id), *packets))
        async def check_data_length():
            current_length = await redis.llen(str(session_id))
            if current_length > MAX_BUFFER_LENGTH:
                await redis.ltrim(str(session_id), int(MAX_BUFFER_LENGTH / 10) , current_length)
        asyncio.ensure_future(check_data_length())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(udp_server())
    loop.close()
