#include "streamController.h"
#include "ADS131M08.h"
#include "ADS131ESP.h"

StreamController *streamController;
ADS131M08 adc;

void setup()
{
  Serial.begin(115200);
  streamController = new StreamController();
  streamController->connect("Pixel", "asdfghjkl");
  adc.begin();
  adc.RESET();
  adc.STANDBY();
  adc.writeReg(ADS131_CLOCK,0b1111111100001110); //Clock register (page 55 in datasheet)
  // /*CLOCK REG SETTINGS
  //  * Bits 15-8: ADC Channel enable/disable
  //  * Bit 7: Crystal disable
  //  * Bit 6: External Reference Enable
  //  * Bit 5: Reserved
  //  * Bits 4-2: Modulator Oversampling 000 = 128 OSR (32ksps), 111 = 16256 OSR (250sps)
  //  * Bits 1-0: Power mode selections 11 or 10 = high resolution, 01 = low power, 00 = very low power
  //  */
  adc.writeReg(ADS131_CFG,0b0000000000000000);
  // //DC Block Filter settings:
  adc.writeReg(ADS131_THRSHLD_LSB,0b0000000000000100);
  // //Channel settings
  adc.writeReg(ADS131_CH0_CFG,0b0000000000000000);
  // //Gain settings, 1-128 (increasing by factor of 2)
  adc.setGain(8);
  adc.WAKEUP();
  delayMicroseconds(50);
  adc.startData();
}

uint8_t maxReading = 0;
void loop()
{

  const int timeBetweenMesurements_us = 500;
  static int lastMeasurementTime = micros();

  uint8_t x[3] = {0};

  if(adc.frameReady() & (micros() - lastMeasurementTime > timeBetweenMesurements_us))
  {
    lastMeasurementTime = micros();
    streamController->addReading(adc.framePointer(), adc.frameSize());
    // streamController->addReading(&(x[0]), 3);
  }

  // // Serial.println("Reading");
  // if(adc.frameReady())
  // {
  //   if (maxReading > 0){
  //     maxReading -= 1;
  //   }
  //   // Serial.println( adc.frameSize());
  //   // lastMeasurementTime = micros();
  //   adc.newFrame();
  //   for(int j = 0; j < 10; j ++){
  //   for (int i = 2; i < 26; i++){
  //     int index = i + j * 33;
  //     uint8_t reading = *(adc.framePointer() + index);
  //     if ((i-2) % 3 == 0){
  //       if (reading & 0x80){
  //         continue;
  //         reading = ~reading;
  //       }
  //       maxReading = reading > maxReading ? reading : maxReading;
  //     }
  //   }
  //   }
  //   Serial.println(maxReading);
  //   // int reading = *adc.framePointer();
  //   // maxReading = reading > maxReading ? reading : maxReading;
  //   // Serial.println(*(adc.framePointer()+2));
  //   // streamController->addReading(adc.framePointer(), adc.frameSize());
  //   // streamController->addReading(&(x[0]), 3);
  // }
}
