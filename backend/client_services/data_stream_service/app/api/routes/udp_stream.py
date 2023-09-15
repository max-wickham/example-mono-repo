import asyncio

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
        message = data.decode()
        with open('/test.txt','w') as file:
            file.write(f"Received data from {addr}: {message}")
        print(f"Received data from {addr}: {message}")

        # # You can add your custom logic here to process the received data

        # # Send a response back to the client (optional)
        # response = f"Received: {message}".encode()
        # self.transport.sendto(response, addr)
