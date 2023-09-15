import asyncio
import base64

from redis.asyncio import from_url


MAX_BUFFER_LENGTH = 200000
PACKETS_SIZE = 48
REDIS_URL = 'redis://127.0.0.1'

redis = from_url('redis://127.0.0.1', decode_responses=True)



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
