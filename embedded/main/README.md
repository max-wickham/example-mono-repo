## Bluetooth Design

- RX
- TX

## Server (Controller by Device)

- Server State
- Server Message Length
- Server Message Hash
- Current Request Endpoint
- Request Retransmit (toggle off then on)

## Client (Controller by Frontend)

- Client State
- Request ID
- Current Request Endpoint
- Client Message Hash
- Request Retransmit (toggle off then on)

### State

- State is an enum of possible values
    - idle
    - transmitting
    - receiving
    - processing

- Response reply architecture
    - Client Transmits Request with endpoint and message ID and request Data
    - Server Receives Request Data and Endpoint
    - Server Replies with message ID and response String

1. Client switches to transmitting state
2. Waits for Server to switch to receiving
3. Client sets the Current Request Endpoint
4. Client waits for the server to match the request endpoint
5. Client sets the message length and sends a message of that length
6. Server receives the message into a buffer of length message length
7. Server switches from receiving to processing
8. Server runs the endpoint function on the message
9. Server switches to transmitting and waits for the Client to switch to transmitting
10. Server transmits response of length server message length and sends to the client
11. Once the client has received the response it sets its state to idle and then the server does the same



- Client send start recording to the device (using a route)

- Device send recording started to the client

- Device does the recording

- Device send recording ready to the client (using a route)

- Client reads the recording from the client (using a route)



- Client requests that readings should be sent

- Device sends reading periodically.
