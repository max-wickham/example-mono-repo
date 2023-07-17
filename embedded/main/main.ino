#include <EEPROM.h>

#include "dataSampler.h"
#include "devBluetoothController.h"


DataSampler dataSampler = DataSampler();
DevBluetoothController devBluetoothController = DevBluetoothController();


void recordingRequestChanged(RecordingStateRequest state_request){
  Serial.println('Recording Request Change');
  Serial.println(state_request);
  if (state_request == RSRStartRequested){
    devBluetoothController.setRecordingState(RSInProgress);
  }
  if (state_request == RSRStopRequested){
    devBluetoothController.setRecordingState(RSComplete);
  }
}

void downloadRequestChanged(DownloadStateRequest state_request){
  Serial.println('Download Request Change');
  Serial.println(state_request);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE work!");
  devBluetoothController.setup();
  dataSampler.setup();

  devBluetoothController.setRecordingRequestStateChangedCallback(recordingRequestChanged);
  devBluetoothController.setDownloadStateRequestChangeCallback(downloadRequestChanged);
}

void loop() {
  // Serial.println("Step");
  devBluetoothController.run();
  // put your main code here, to run repeatedly:
  // delay(1);
  // delay(2000);
}

// 1. need to be able to make a connection to a device
// 2. need to be able to start streaming data at a certain frequency
// 3. need to be told to start recording data into a RAM block
// 4. need to stop recording data after a certain amount of time
// 5. need to be able to notify when recording is finished
// 6. need to be able to download the recording and the has of the recording
