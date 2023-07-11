#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/
// #define SERVICE_UUID                    "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
// #define CHARACTERISTIC_UUID             "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define READING_SERVICE                 "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CURRENT_READING_CHARACTERISTIC  "beb5483e-36e1-4688-b7f5-ea07361b26a8"
// characteristics

    // is recording
    // user desired recording state

    // user wants readings to be streamed
    // current reading

    // user wants recording

enum RecordingState {
    noRecording,
    startRequested,
    inProgress,
    stopRequested,
    complete,
};

// BLECharacteristic bmeHumidityCharacteristics(CURRENT_READING_CHARACTERISTIC, BLECharacteristic::PROPERTY_NOTIFY);
class DevBluetoothController{
    BLEServer *pServer;
    BLEService *reading_service;
    BLECharacteristic *current_reading_characteristic;
    BLEAdvertising *pAdvertising;
    public:

    void setup () {
        BLEDevice::init("MindFeed");
        pServer = BLEDevice::createServer();
        Serial.println("Server Made");
        reading_service = pServer->createService(READING_SERVICE);
        current_reading_characteristic = reading_service->createCharacteristic(
                                                CURRENT_READING_CHARACTERISTIC,
                                                BLECharacteristic::PROPERTY_READ |
                                                BLECharacteristic::PROPERTY_BROADCAST |
                                                BLECharacteristic::PROPERTY_INDICATE |
                                                BLECharacteristic::PROPERTY_NOTIFY
                                            );
        BLEDescriptor *current_reading_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint16_t)0x2902));
        int data = 0;
        current_reading_characteristic->setValue("test");
        current_reading_characteristic->addDescriptor(current_reading_characteristic_descriptor);

        reading_service->start();
        // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
        pAdvertising = BLEDevice::getAdvertising();
        pAdvertising->addServiceUUID(READING_SERVICE);
        pAdvertising->setScanResponse(true);
        pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
        pAdvertising->setMinPreferred(0x12);
        pServer->getAdvertising()->start();
        BLEDevice::startAdvertising();
        Serial.println("Characteristic defined! Now you can read it in your phone!");
    }

    bool isConnected() {
        // return true if connected to the user
        return pServer->getConnectedCount() > 0;
    }

    //////////////////

    bool getStartRecording() {
        // check if the user has set start recording

        // use the recordingState
            // return true if this is currently in a start recording state
    }

    bool getStopRecording() {
        // check if the user has set stop recording

        // use the recordingState
            // return true if this is currently in a stop recording state
    }

    void setRecordingState (bool isRecording) {
        // set the current recording state of the device

        // use the recordingState
            // set to inProgress if true else complete if false

        // can only set to inProgress if the current state is requestRecording
        // can only be set to complete if the current state is inProgress
    }

    //////////////////

    bool requestReadings() {
        // return true if the user want readings to be sent
    }

    void setCurrentReading() {
        // set the current reading to be sent to the user
    }

    //////////////////

    bool requestRecording() {
        // return true is the user has requested a download
    }

    void sendRecording() {
        // send a recording to the user
    }

    // TODO callbacks for start and stop recording

    void run() {
        static int count = 0;
        static unsigned long last_reading_update = 0;
        count += 1;

        if (millis() - last_reading_update > 100){
            // console.log('sending');
            Serial.println(count);
            last_reading_update = millis();
            current_reading_characteristic->setValue(count);
            current_reading_characteristic->notify();
        }
    }

};
