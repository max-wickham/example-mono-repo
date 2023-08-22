#ifndef DEV_BLUETOOTH_CONTROLLER
#define DEV_BLUETOOTH_CONTROLLER

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <unordered_map>

// Server Characteristics
#define SERVER_SERVICE "b9908bbc-de94-42fb-952a-b4593d12ebd1"
#define SERVER_STATE "99497f04-e714-476e-9f2b-087785ba0315"
#define SERVER_CURRENT_ENDPOINT "1fcdb326-0779-4aed-b50b-d0b21e00c277"

// Client Characteristics
#define CLIENT_SERVICE "ce2bd191-c2b9-4e02-964c-0a0bd7e421da"
#define CLIENT_STATE "b44c49de-4751-439c-8ea7-c3bc2516aa3c"
#define CLIENT_CURRENT_ENDPOINT "7f853ef2-ba92-4c0a-bf53-b7dd876f0153"

// Common Characteristics
#define COMMON_SERVICE "18d55f53-142a-4f7a-9874-e70f8ff7e385"
#define MESSAGE_LENGTH "8018a468-562c-4b09-9b7c-60935f0b26c4"
#define MESSAGE_HASH "2c6c0afb-030c-42d1-88e0-950616111bdc"
#define REQUEST_RETRANSMIT "765c0ac1-ed04-48af-997a-dc56d3dad788"
#define TX "f45bb166-b718-4f3e-865c-c9804a06f6b5"
#define RX "4463d9f3-911d-424f-ab17-af0ebc9ef236"
#define MESSAGE_ID "b66dca04-4a62-4367-b854-6b511ce903d1"

enum ClientServerState
{
    Idle,
    Transmitting,
    Receiving,
    Processing,
};

struct File {
    uint32_t start_address;
    uint32_t file_size;
};

class ServerCallbacks : public BLEServerCallbacks
{
    void onConnect(BLEServer *pServer){
        // handle connection
    };

    void onDisconnect(BLEServer *pServer)
    {
        // handle disconnection
    }
};

class TextToTextRouteCallback {
    /*Receive a string and respond with a string*/

    virtual std::string callback(std::string message) = 0;

};

class TextToFileRouteCallback {
    /*Receive a string and respond with a file*/

    virtual File callback(std::string message) = 0;

};

class FileToTextRouteCallback {
    /*Receive a file and respond with a string*/

    virtual std::string callback(File &file) = 0;

};

class DevBluetoothController
{
    struct {
        enum {RecNull, RecText, RecFile} receiving_type = RecNull;
        unsigned int receiving_index = 0;
        std::string receiving_text = "";
    } receiving_state;

    static const unsigned int packet_size = 400;

    std::unordered_map <std::string, TextToTextRouteCallback*> text_to_text_callbacks;
    std::unordered_map <std::string, TextToFileRouteCallback*> text_to_file_callbacks;
    std::unordered_map <std::string, FileToTextRouteCallback*> file_to_text_callbacks;

    BLEServer *pServer;

    BLEService *server_service;
    BLECharacteristic *server_state_char;
    BLECharacteristic *server_current_endpoint_char;

    BLEService *client_service;
    BLECharacteristic *client_state_char;
    BLECharacteristic *client_current_endpoint_char;

    BLEService *common_service;
    BLECharacteristic *message_length_char;
    BLECharacteristic *message_hash_char;
    BLECharacteristic *request_retransmit_char;
    BLECharacteristic *tx_char;
    BLECharacteristic *rx_char;
    BLECharacteristic *message_id_char;

    BLEAdvertising *pAdvertising;

    void configure_characteristic(BLEService *service, BLECharacteristic *&characteristic, uint32_t properties, char *uuid)
    {
        characteristic = service->createCharacteristic(
            uuid,
            properties);
        BLEDescriptor *descriptor = new BLEDescriptor(BLEUUID(uuid));
        characteristic->addDescriptor(descriptor);
    }

    void set_server_state(ClientServerState state)
    {
        int val = static_cast<int>(state);
        server_state_char->setValue(val);
        server_state_char->notify();
    }

    ClientServerState get_server_state()
    {
        // TODO
    }

    void set_endpoint(std::string endpoint)
    {
        // uint32_t hash = std::hash<std::string>{}(endpoint);
        server_current_endpoint_char->setValue(endpoint);
        server_current_endpoint_char->notify();
    }

    void set_message_hash_and_length(std::string message)
    {
        uint32_t message_hash = std::hash<std::string>{}(message);
        uint32_t message_length = message.length();
        message_hash_char->setValue(message_hash);
        message_hash_char->notify();
        message_length_char->setValue(message_length);
        message_length_char->notify();
    }

    uint32_t get_message_length() {

    }

    ClientServerState get_client_state()
    {
        // TODO
    }

    bool client_connected()
    {
        // TODO
    }

public:
    void setup()
    {
        BLEDevice::init("MindFeed");
        pServer = BLEDevice::createServer();
        pServer->setCallbacks(new ServerCallbacks());

        // Server Service
        const uint32_t server_props = BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_BROADCAST | BLECharacteristic::PROPERTY_INDICATE | BLECharacteristic::PROPERTY_NOTIFY;
        server_service = pServer->createService(SERVER_SERVICE);
        configure_characteristic(server_service, server_state_char, server_props, SERVER_STATE);
        configure_characteristic(server_service, server_current_endpoint_char, server_props, SERVER_CURRENT_ENDPOINT);

        // Client Service
        client_service = pServer->createService(CLIENT_SERVICE);
        const uint32_t client_props = BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_BROADCAST | BLECharacteristic::PROPERTY_INDICATE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE;
        configure_characteristic(server_service, server_state_char, client_props, CLIENT_STATE);
        configure_characteristic(server_service, server_current_endpoint_char, client_props, CLIENT_CURRENT_ENDPOINT);

        // Common Service
        common_service = pServer->createService(COMMON_SERVICE);
        const uint32_t client_props = BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_BROADCAST | BLECharacteristic::PROPERTY_INDICATE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE;
        configure_characteristic(server_service, message_length_char, client_props, MESSAGE_LENGTH);
        configure_characteristic(server_service, message_hash_char, client_props, MESSAGE_HASH);
        configure_characteristic(server_service, request_retransmit_char, client_props, REQUEST_RETRANSMIT);
        configure_characteristic(server_service, rx_char, client_props, RX);
        configure_characteristic(server_service, tx_char, client_props, TX);
        configure_characteristic(server_service, message_id_char, client_props, MESSAGE_ID);

        server_service->start();
        client_service->start();
        common_service->start();

        pAdvertising = BLEDevice::getAdvertising();
        pAdvertising->addServiceUUID(SERVER_SERVICE);
        pAdvertising->addServiceUUID(CLIENT_SERVICE);
        pAdvertising->addServiceUUID(COMMON_SERVICE);
        pAdvertising->setScanResponse(true);
        pAdvertising->setMinPreferred(0x06); // functions that help with iPhone connections issue
        pAdvertising->setMinPreferred(0x12);
        pServer->getAdvertising()->start();
        BLEDevice::startAdvertising();
    }

    bool send_message(std::string route, std::string message, uint timeout_s = 1)
    { // send the given string to the required route
        unsigned long start_time_ms = millis();
        // (this should all happen in void run if we want to create non blocking code)

        // check if the client is connected and idle otherwise return nothing
        if (!client_connected() && get_client_state() == Idle)
        {
            return false;
        }
        // switch from idle to transmitting
        set_server_state(Transmitting);
        // set the message length, hash, and endpoint information
        set_message_hash_and_length(message);
        // wait until the client has switched to the same endpoint
        while (!(client_current_endpoint_char->getValue() == server_current_endpoint_char->getValue()) && get_client_state() == Receiving)
        {
            if (millis() - start_time_ms < timeout_s * 1000)
            {
                return false;
            }
        }
        // send the message to the client
        for (int i = 0; i < message.length(); i += packet_size)
        {
            std::string packet = message.substr(0, 400);
            tx_char->setValue(packet);
            tx_char->notify();
            // sleep(1);
        }
        // TODO resend message logic
        set_server_state(Idle);
    }

    void add_route(std::string route, TextToTextRouteCallback *callback_class)
    {
        text_to_text_callbacks[route] = callback_class;
    }

    void add_route(std::string route, TextToFileRouteCallback *callback_class)
    {
        text_to_file_callbacks[route] = callback_class;
    }

    void add_route(std::string route, FileToTextRouteCallback *callback_class)
    {
        file_to_text_callbacks[route] = callback_class;
    }

    void message_id_change_callback() {
        if (get_server_state() == Idle && get_client_state() == Transmitting) {
            set_server_state(Receiving);
            const std::string endpoint = client_current_endpoint_char->getValue();
            server_current_endpoint_char->setValue(endpoint);

            // reset the current receiving state
        }
    }

    void tx_change_callback(std::string packet) {

        if (receiving_state.receiving_type = receiving_state.RecText){
            receiving_state.receiving_text += packet;
            receiving_state.receiving_index += packet.length();
        }

        // check the current receiving type (file or text)

        // append to file or text the packet

        if (receiving_state.receiving_index >= get_message_length()){
            // check the hash is correct
            // find the current callback
            // run the current callback
            // respond with the text or file from the callback
        }
        // check if the message length is correct

            // check if the message hash is correct

            // find the current callback

            // run the current callback

            // respond with the text or file information
    }


};

#endif
