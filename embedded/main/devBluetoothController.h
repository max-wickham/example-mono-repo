#ifndef DEV_BLUETOOTH_CONTROLLER
#define DEV_BLUETOOTH_CONTROLLER

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <EEPROM.h>
#include <unordered_map>
#include "Configs.h"

// Server Characteristics
#define SERVER_SERVICE "b9908bbc-de94-42fb-952a-b4593d12ebd1"
#define SERVER_MESSAGE "99497f04-e714-476e-9f2b-087785ba0315"
#define SERVER_CURRENT_ENDPOINT "1fcdb326-0779-4aed-b50b-d0b21e00c277"
#define SERVER_FILENAME "80e11a85-32ff-4df0-b03b-6212b71d8f49"

// Client Characteristics
#define CLIENT_SERVICE "ce2bd191-c2b9-4e02-964c-0a0bd7e421da"
#define CLIENT_MESSAGE "b44c49de-4751-439c-8ea7-c3bc2516aa3c"
#define CLIENT_CURRENT_ENDPOINT "7f853ef2-ba92-4c0a-bf53-b7dd876f0153"
#define CLIENT_RECEIVING "58813e28-4aa6-4e99-abf7-d5f198cfd819"

#define RX_SERVICE "d03e19c1-457e-456c-b1d1-48f335302858"
#define CLIENT_RX "2aa577c5-a852-487c-8e01-1237a093a0be"

#define PACKET_SIZE 200

char packet[PACKET_SIZE] = {0};

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

class MessageCallbacks
{

public:
    virtual void callback(std::string message) = 0;
};

class DevBluetoothController
{
    class ServerCharCallbacks : public BLECharacteristicCallbacks
    {
    protected:
        virtual void onWrite(BLECharacteristic *pCharacteristic) = 0;

        void onRead(BLECharacteristic *pCharacteristic)
        {
            // handle the read operation
        }
        DevBluetoothController *controller;

    public:
        ServerCharCallbacks(DevBluetoothController *controller)
        {
            this->controller = controller;
        }
    };
    class ServerMessageCallbacks : public ServerCharCallbacks
    {
        using ServerCharCallbacks::ServerCharCallbacks;
        void onWrite(BLECharacteristic *pCharacteristic);
    };

    class ServerFileNameCallbacks : public ServerCharCallbacks
    {
        using ServerCharCallbacks::ServerCharCallbacks;
        void onWrite(BLECharacteristic *pCharacteristic);
    };

    struct
    {
        bool uploading = false;
        int file_state_address = 0;
        int file_index = 0;
        int file_length = 0;
    } upload_state;

    std::unordered_map<std::string, MessageCallbacks *> message_callbacks;

    std::unordered_map<std::string, int> file_locations;

    BLEServer *pServer;
    BLEService *server_service;
    BLECharacteristic *server_message_char;
    BLECharacteristic *server_current_endpoint_char;
    BLECharacteristic *server_filename_char;
    BLEService *client_service;
    BLECharacteristic *client_message_char;
    BLECharacteristic *client_current_endpoint_char;
    BLECharacteristic *client_receiving_char;
    BLEService *rx_service;
    BLECharacteristic *client_rx_char;
    ServerMessageCallbacks *server_message_callbacks = new ServerMessageCallbacks(this);
    ServerFileNameCallbacks *server_filename_callbacks = new ServerFileNameCallbacks(this);

    BLEAdvertising *pAdvertising;

    void configure_characteristic(BLEService *service, BLECharacteristic *&characteristic, uint32_t properties, char *uuid)
    {
        characteristic = service->createCharacteristic(
            uuid,
            properties);
        BLEDescriptor *descriptor = new BLEDescriptor(BLEUUID(uuid));
        characteristic->addDescriptor(descriptor);
    }

public:
    void setup()
    {
        BLEDevice::init("MindFeed");
        pServer = BLEDevice::createServer();
        pServer->setCallbacks(new ServerCallbacks());

        // Server Service
        const uint32_t server_props = BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_BROADCAST | BLECharacteristic::PROPERTY_INDICATE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE;
        server_service = pServer->createService(SERVER_SERVICE);
        configure_characteristic(server_service, server_message_char, server_props, SERVER_MESSAGE);
        configure_characteristic(server_service, server_current_endpoint_char, server_props, SERVER_CURRENT_ENDPOINT);
        configure_characteristic(server_service, server_filename_char, server_props, SERVER_FILENAME);
        server_message_char->setCallbacks(server_message_callbacks);
        server_filename_char->setCallbacks(server_filename_callbacks);

        // Client Service
        client_service = pServer->createService(CLIENT_SERVICE);
        const uint32_t client_props = BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_BROADCAST | BLECharacteristic::PROPERTY_INDICATE | BLECharacteristic::PROPERTY_NOTIFY;
        configure_characteristic(client_service, client_message_char, client_props, CLIENT_MESSAGE);
        configure_characteristic(client_service, client_current_endpoint_char, client_props, CLIENT_CURRENT_ENDPOINT);
        configure_characteristic(client_service, client_receiving_char, client_props, CLIENT_RECEIVING);

        //RX Service
        rx_service = pServer->createService(RX_SERVICE);
        configure_characteristic(rx_service, client_rx_char, client_props, CLIENT_RX);

        // Add the stored general service items

        server_service->start();
        client_service->start();
        server_service->start();

        pAdvertising = BLEDevice::getAdvertising();
        pAdvertising->addServiceUUID(SERVER_SERVICE);
        pAdvertising->addServiceUUID(CLIENT_SERVICE);
        pAdvertising->addServiceUUID(RX_SERVICE);
        pAdvertising->setScanResponse(true);
        pAdvertising->setMinPreferred(0x06); // functions that help with iPhone connections issue
        pAdvertising->setMinPreferred(0x12);
        pServer->getAdvertising()->start();
        BLEDevice::startAdvertising();
    }

    void addCallback(std::string endpoint, MessageCallbacks *callback)
    {
        message_callbacks[endpoint] = callback;
    }

    void addFile(std::string fileName, int fileLocation)
    {
        file_locations[fileName] = fileLocation;
    }

    void sendMessage(std::string endpoint, std::string message)
    {
        client_current_endpoint_char->setValue(endpoint);
        client_current_endpoint_char->notify();
        client_message_char->setValue(message);
        client_message_char->notify();
    }

    void run()
    {
        if (upload_state.uploading)
        {
            if (upload_state.file_index >= upload_state.file_length)
            {
                Serial.println("Finished");
                // TODO done
                upload_state.uploading = false;
                upload_state.file_index = 0;
                upload_state.file_length = 0;
                client_receiving_char->setValue("false");
                client_receiving_char->notify();
            }
            else
            {
                Serial.println("Sending Packet");
                Serial.println(upload_state.file_index);
                const int index = upload_state.file_index;
                int i = index;
                const int packetLength = PACKET_SIZE > upload_state.file_length - index ?
                    upload_state.file_length - index : PACKET_SIZE;
                Serial.println(packetLength);
                for (; i < packetLength; i++)
                {
                    packet[i] = EEPROM.readByte(index + i);
                }
                upload_state.file_index = i + index;
                // Now can write the packet on the rx line
                char *packet_address = &(packet[0]);
                uint8_t *data = reinterpret_cast<uint8_t *>(packet_address);
                size_t length = packetLength;
                Serial.println("packet length");
                Serial.println(length);
                client_rx_char->setValue(data, length);
                client_rx_char->notify();
                Serial.println("sent data");
            }
        }
    }
};

void DevBluetoothController::ServerMessageCallbacks::onWrite(BLECharacteristic *pCharacteristic)
{
    std::string message = pCharacteristic->getValue();
    std::string endpoint = controller->server_current_endpoint_char->getValue();
    // Serial.print("Message: ");
    // Serial.println(message.c_str());
    // Serial.print("Endpoint: ");
    // Serial.println(endpoint.c_str());
    MessageCallbacks *callback = controller->message_callbacks[endpoint];
    callback->callback(message);
}

void DevBluetoothController::ServerFileNameCallbacks::onWrite(BLECharacteristic *pCharacteristic)
{
    std::string filename = pCharacteristic->getValue();
    Serial.print("filename: ");
    Serial.println(filename.c_str());
    const int file_location = controller->file_locations[filename];
    const int file_length = EEPROM.readInt(file_location);
    const int file_start_address = file_location + 4;
    controller->upload_state.file_length = file_length;
    controller->upload_state.uploading = true;
    controller->upload_state.file_state_address = file_start_address;
    controller->upload_state.file_index = 0;
    controller->client_receiving_char->setValue("true");
    controller->client_receiving_char->notify();
    delay(20);
}

// Send a file and receive a file

#endif
