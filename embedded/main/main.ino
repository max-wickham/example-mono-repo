// #include <EEPROM.h>

// #include "devBluetoothController2.h"
// #include "dataManager.h"

// DataManager *dataManager = new DataManager();
// DevBluetoothController *devBluetoothController = new DevBluetoothController(dataManager);

// bool isRecording = false;

// class StateChangeCallbacks : public BluetoothStateChangeCallbacks
// {
//   void recordingStateRequestChangeCallback(RecordingStateRequest &state) override
//   {
//     // callback to run when the client requests a recording state change
//     Serial.println("Recording Request Change");
//     Serial.println(state);

//     if (state == RSRStartRequested)
//     {
//       // tell the client the recording has started
//       devBluetoothController->setRecordingState(RSInProgress);
//       isRecording = true;
//     }
//     if (state == RSRStopRequested)
//     {
//       // tell the client the recording has stopped
//       devBluetoothController->setRecordingState(RSComplete);
//       isRecording = false;
//       // compute the feature extraction on the recorded data
//       dataManager->doFeatureExtraction();
//     }
//   }

//   void downloadStateRequestChangeCallback(DownloadStateRequest &state) override
//   {
//     Serial.println("Download Request Change");
//     Serial.println(state);
//     // tell the bluetooth controller the data from the dataManager
//     devBluetoothController->uploadData();
//   }
// };

// StateChangeCallbacks *callbacks = new StateChangeCallbacks();

// void setup()
// {
//   Serial.begin(115200);
//   Serial.println("Starting BLE work!");

//   // setup the bluetooth controller
//   devBluetoothController->setup();
//   devBluetoothController->setStateChangeCallbacks(callbacks);
// }

// class TestCallback : public TextToTextRouteCallback {
//     public:
//     std::string callback(std::string message) override {
//       return "hello";
//     }
// };

// void loop()
// {

//   DevBluetoothController *controller = new DevBluetoothController();

//   controller->setup();
//   controller->add_route("/hi",  new TestCallback());

//   static long recording_start_time = 0;
//   static int count = 0;
//   static int lastReadingMillis;
//   static const int liveReadingTransmitTimePeriod_ms = 100; // transmit 10 times per second (every 100ms)

//   // example of keeping the recording alive for 10 second
//   if (!isRecording)
//   {
//     recording_start_time = millis();
//   }
//   else
//   {
//     if (millis() - recording_start_time > 1000)
//     {
//       Serial.println('Stopping Recording');
//       devBluetoothController->setRecordingState(RSComplete);
//       isRecording = false;
//     }
//   }

//   // Run the bluetooth controller
//   devBluetoothController->run();

//   if (isRecording)
//   {
//     // TODO @teo create an instance of the reading packet struct and send it to the server
//     // ReadingPacket packet = {};
//     // dataManager->addPacket(packet)
//   }

//   if (millis() > lastReadingMillis + liveReadingTransmitTimePeriod_ms)
//   {
//     count += 1;
//     lastReadingMillis += liveReadingTransmitTimePeriod_ms;
//     // TODO @teo put a single channel value in here as an int, (I will convert to support full channels)
//     int readingValue = count;
//     devBluetoothController->setReading(readingValue);
//   }
// }

#include <EEPROM.h>
#include "devBluetoothController3.h"

#define EEPROM_SIZE 1000

class TestCallbacks : public MessageCallbacks
{
  DevBluetoothController *controller;

public:
  TestCallbacks(DevBluetoothController *controller)
  {
    this->controller = controller;
  }

  void callback(std::string message) override
  {
    Serial.println(message.c_str());
    delay(100);
    Serial.println("Running Callback");
    controller->sendMessage("/test_response","response message");
  }
};
DevBluetoothController *controller;
void setup()
{
  Serial.begin(115200);
  // initiliase the EEPROM
  EEPROM.begin(EEPROM_SIZE);

  // create a fake file
  const int testFileLocation = 100;
  const int testFileLength = 1000;
  EEPROM.writeInt(testFileLocation, testFileLength);
  for (int i = 0; i < 1000; i++){
    EEPROM.writeByte(i + testFileLocation + 4, (char)i);
  }


  controller = new DevBluetoothController();
  controller->addCallback("/test", new TestCallbacks(controller));
  controller->addFile("test_file", testFileLocation);
  controller->setup();
  Serial.println("Setup Complete");
}

void loop()
{
  controller->run();
}
