#include <EEPROM.h>

#include "dataSampler.h"
#include "devBluetoothController.h"


DataSampler dataSampler = DataSampler();
DevBluetoothController devBluetoothController = DevBluetoothController();

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE work!");
  devBluetoothController.setup();
  dataSampler.setup();
}

void loop() {
  // Serial.println("Step");
  devBluetoothController.run();
  // put your main code here, to run repeatedly:
  delay(100);
  // delay(2000);
}

// 1. need to be able to make a connection to a device
// 2. need to be able to start streaming data at a certain frequency
// 3. need to be told to start recording data into a RAM block
// 4. need to stop recording data after a certain amount of time
// 5. need to be able to notify when recording is finished
// 6. need to be able to download the recording and the has of the recording
