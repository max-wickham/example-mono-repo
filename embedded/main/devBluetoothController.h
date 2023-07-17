#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>


#define READING_SERVICE "99497f04-e714-476e-9f2b-087785ba0315"
#define CURRENT_READING_CHARACTERISTIC "8018a468-562c-4b09-9b7c-60935f0b26c4"

#define RECORDING_STATE_SERVICE "2c6c0afb-030c-42d1-88e0-950616111bdc"
#define RECORDING_STATE_CHARACTERISTIC "1fcdb326-0779-4aed-b50b-d0b21e00c277"
#define RECORDING_REQUEST_CHARACTERISTIC "765c0ac1-ed04-48af-997a-dc56d3dad788"

#define RECORDING_DOWNLOAD_SERVICE "b44c49de-4751-439c-8ea7-c3bc2516aa3c"
#define DOWNLOAD_REQUEST_CHARACTERISTIC "7f853ef2-ba92-4c0a-bf53-b7dd876f0153"
#define DOWNLOAD_PROGRESS_CHARACTERISTIC "fddd103d-55d8-4d92-be4f-09c8b56280ef"
#define RECORDING_HASH_CHARACTERISTIC "f45bb166-b718-4f3e-865c-c9804a06f6b5"
#define TX_CHARACTERISTIC "4463d9f3-911d-424f-ab17-af0ebc9ef236"

/*
This is the recording state of the ESP32, synced to the client using bluetooth characteristic
*/
enum RecordingState
{
    RSNotRecording,
    RSInProgress,
    RSComplete,
};

/*
This is used by the client to send state requests to the ESP32 in order to control the recording state
*/
enum RecordingStateRequest
{
    RSRStartRequested,
    RSRStopRequested,
};

/*
This is the download state of the server, (showing whether an upload to the client is in progress)
*/
enum DownloadState
{
    DSStopped,
    DSInProgress,
    DSComplete,
};

// This is used be the client to send state requests to the ESP32 in order to control the recording download state
enum DownloadStateRequest
{
    DSRStartRequested,
    DSRNotRequested,
};

class ServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      // handle connection
    };

    void onDisconnect(BLEServer* pServer) {
      // handle disconnection
    }
};

class RecordingStateRequestCallbacks: public BLECharacteristicCallbacks {
    DevBluetoothController *controller;

    /*
    The data received here is a RecordingStateRequest and tells the ESP32 to start or stop recording
    */
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();
      if (value.length() > 0) {
        // handle the value written by the client
      }
    }

    void onRead(BLECharacteristic *pCharacteristic) {
      // handle the read operation
    }

    public:
    RecordingStateRequestCallbacks(DevBluetoothController *controller){
        controller = controller;
    }
};

class DownloadStateRequestCallbacks: public BLECharacteristicCallbacks {
    DevBluetoothController *controller;

    /*
    The data received here is a DownloadStateRequest and tells the ESP32 to start or stop sending recordings to the client
    */
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string value = pCharacteristic->getValue();
      if (value.length() > 0) {
        // handle the value written by the client
      }
    }

    void onRead(BLECharacteristic *pCharacteristic) {
      // handle the read operation
    }

    public:
    DownloadStateRequestCallbacks(DevBluetoothController *controller){
        controller = controller;
    }
};


// BLECharacteristic bmeHumidityCharacteristics(CURRENT_READING_CHARACTERISTIC, BLECharacteristic::PROPERTY_NOTIFY);
class DevBluetoothController
{
    BLEServer *pServer;
    BLEService *reading_service;
    // Gives the client access to the current sensor reading
    BLECharacteristic *current_reading_characteristic;

    BLEService *recording_state_service;
    // Tells the client the current recording state (stopped, in progress or complete)
    BLECharacteristic *recording_state_characteristic;
    // Used by the client to requests recording state changes
    BLECharacteristic *recording_request_characteristic;

    BLEService *recording_download_service;
    // Current state of recording upload to the client
    BLECharacteristic *download_request_characteristic;
    // Used by the client to request recording downloads
    BLECharacteristic *download_state_progress_characteristic;
    // The expected hash of the current recording, read by the client to ensure successful download
    BLECharacteristic *recording_hash_characteristic;
    // The TX channel over which recordings are sent
    BLECharacteristic *tx_characteristic;

    BLEAdvertising *pAdvertising;

    // This callback is run when the client requests a recording state change and can be set in the main script
    void (*recording_state_request_change_callback)(RecordingStateRequest state_request);
    // This callback is run when the client requests a download and can be set in the main script
    void (*download_state_request_change_callback)(DownloadStateRequest state_request);

    RecordingState currentRecordingState = RSNotRecording;
    DownloadState currentDownloadState = DSStopped;

    void _recording_state_request_callback(
        BLERemoteCharacteristic* pBLERemoteCharacteristic,
        uint8_t* pData,
        size_t length,
        bool isNotify
    ){
        this->recording_state_request_change_callback(static_cast<RecordingStateRequest>(*pData));
    }

    void _download_state_request_callback(
        BLERemoteCharacteristic* pBLERemoteCharacteristic,
        uint8_t* pData,
        size_t length,
        bool isNotify
    ){
        this->download_state_request_change_callback(static_cast<DownloadStateRequest>(*pData));
    }

public:
    void setup()
    {
        BLEDevice::init("MindFeed");
        pServer = BLEDevice::createServer();
        pServer->setCallbacks(new ServerCallbacks());
        Serial.println("Server Made");

        ///// Reading Service
        reading_service = pServer->createService(READING_SERVICE);
        current_reading_characteristic = reading_service->createCharacteristic(
            CURRENT_READING_CHARACTERISTIC,
            BLECharacteristic::PROPERTY_READ |
                BLECharacteristic::PROPERTY_BROADCAST |
                BLECharacteristic::PROPERTY_INDICATE |
                BLECharacteristic::PROPERTY_NOTIFY);
        BLEDescriptor *current_reading_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint32_t)0x2902));
        int data = 0;
        // current_reading_characteristic->setValue(0);
        current_reading_characteristic->addDescriptor(current_reading_characteristic_descriptor);




        ///// Recording Control service
        recording_state_service = pServer->createService(RECORDING_STATE_SERVICE);

        recording_state_characteristic = reading_service->createCharacteristic(
            RECORDING_STATE_CHARACTERISTIC,
            BLECharacteristic::PROPERTY_READ |
                BLECharacteristic::PROPERTY_WRITE |
                BLECharacteristic::PROPERTY_BROADCAST |
                BLECharacteristic::PROPERTY_INDICATE |
                BLECharacteristic::PROPERTY_NOTIFY);
        BLEDescriptor *recording_state_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint32_t)0x2903));
        recording_state_characteristic->addDescriptor(recording_state_characteristic_descriptor);

        recording_request_characteristic = reading_service->createCharacteristic(
            RECORDING_REQUEST_CHARACTERISTIC,
            BLECharacteristic::PROPERTY_READ |
                BLECharacteristic::PROPERTY_WRITE |
                BLECharacteristic::PROPERTY_BROADCAST |
                BLECharacteristic::PROPERTY_INDICATE |
                BLECharacteristic::PROPERTY_NOTIFY);
        BLEDescriptor *recording_request_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint32_t)0x2904));
        recording_request_characteristic->addDescriptor(recording_request_characteristic_descriptor);
        recording_request_characteristic->setCallbacks(new RecordingStateRequestCallbacks(this));
        // recording_request_characteristic->(_recording_state_request_callback);



        ///// Download Service
        recording_download_service = pServer->createService(RECORDING_DOWNLOAD_SERVICE);

        download_request_characteristic = reading_service->createCharacteristic(
            DOWNLOAD_REQUEST_CHARACTERISTIC,
            BLECharacteristic::PROPERTY_READ |
                BLECharacteristic::PROPERTY_WRITE |
                BLECharacteristic::PROPERTY_BROADCAST |
                BLECharacteristic::PROPERTY_INDICATE |
                BLECharacteristic::PROPERTY_NOTIFY);
        BLEDescriptor *download_request_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint32_t)0x2905));
        download_request_characteristic->addDescriptor(download_request_characteristic_descriptor);

        download_state_progress_characteristic = reading_service->createCharacteristic(
            DOWNLOAD_PROGRESS_CHARACTERISTIC,
            BLECharacteristic::PROPERTY_READ |
                BLECharacteristic::PROPERTY_WRITE |
                BLECharacteristic::PROPERTY_BROADCAST |
                BLECharacteristic::PROPERTY_INDICATE |
                BLECharacteristic::PROPERTY_NOTIFY);
        BLEDescriptor *download_state_progress_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint32_t)0x2906));
        download_state_progress_characteristic->addDescriptor(download_state_progress_characteristic_descriptor);
        download_state_progress_characteristic->setCallbacks(new DownloadStateRequestCallbacks(this));

        recording_hash_characteristic = reading_service->createCharacteristic(
            RECORDING_HASH_CHARACTERISTIC,
            BLECharacteristic::PROPERTY_READ |
                BLECharacteristic::PROPERTY_WRITE |
                BLECharacteristic::PROPERTY_BROADCAST |
                BLECharacteristic::PROPERTY_INDICATE |
                BLECharacteristic::PROPERTY_NOTIFY);
        BLEDescriptor *recording_hash_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint32_t)0x2907));
        recording_hash_characteristic->addDescriptor(recording_hash_characteristic_descriptor);


        tx_characteristic = reading_service->createCharacteristic(
            TX_CHARACTERISTIC,
            BLECharacteristic::PROPERTY_READ |
                BLECharacteristic::PROPERTY_WRITE |
                BLECharacteristic::PROPERTY_BROADCAST |
                BLECharacteristic::PROPERTY_INDICATE |
                BLECharacteristic::PROPERTY_NOTIFY);
        BLEDescriptor *tx_characteristic_descriptor = new BLEDescriptor(BLEUUID((uint32_t)0x2907));
        tx_characteristic->addDescriptor(tx_characteristic_descriptor);





        reading_service->start();
        recording_state_service->start();
        recording_download_service->start();
        // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
        pAdvertising = BLEDevice::getAdvertising();
        pAdvertising->addServiceUUID(READING_SERVICE);
        pAdvertising->addServiceUUID(RECORDING_STATE_SERVICE);
        pAdvertising->addServiceUUID(RECORDING_DOWNLOAD_SERVICE);
        pAdvertising->setScanResponse(true);
        pAdvertising->setMinPreferred(0x06); // functions that help with iPhone connections issue
        pAdvertising->setMinPreferred(0x12);
        pServer->getAdvertising()->start();
        BLEDevice::startAdvertising();
        Serial.println("Characteristic defined! Now you can read it in your phone!");


    }

    bool isConnected()
    {
        // return true if connected to the user
        return pServer->getConnectedCount() > 0;
    }

    ////////////////// Readings

    void setReading(int reading){
        // TODO store and transfer to the bluetooth device
        current_reading_characteristic->setValue(reading);
        current_reading_characteristic->notify();
    }

    ////////////////// Recording Management

    void setRecordingRequestStateChangedCallback(void (*callback)(RecordingStateRequest state_request)){
        recording_state_request_change_callback = callback;
    }

    RecordingStateRequest getRecordingStateRequest()
    {
        return RSRStartRequested;
        // check if the user has set start recording

        // use the recordingState
        // return true if this is currently in a start recording state
    }

    // set whether or not currently recording
    void setRecordingState(RecordingState state){
        int val = static_cast<int>(state);
        // store the recording state and transfer it in bluetooth
        recording_state_characteristic->setValue(val);
        recording_state_characteristic->notify();
    }

    ////////////////// Recording Download Management

    void setDownloadStateRequestChangeCallback(void (*callback)(DownloadStateRequest state_request)){
        download_state_request_change_callback = callback;
    }

    DownloadStateRequest getDownloadStateRequest(){
        return DSRNotRequested;
    }



    // void setDownloadState(DownloadState state){
    //     // store and send via bluetooth
    // }

    // TODO method to allow sending of the actual file

    void run()
    {
        static int count = 0;
        static unsigned long last_reading_update = 0;
        count += 1;
        if (millis() > 2000)
        {
            current_reading_characteristic->setValue(count);
            current_reading_characteristic->notify();
        }
        // if (millis() - last_reading_update > 100){
        // console.log('sending');
        //     Serial.println(count);
        //     last_reading_update = millis();
        //     current_reading_characteristic->setValue(count);
        //     current_reading_characteristic->notify();
        // }
    }
};
