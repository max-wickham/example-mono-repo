#include "streamController.h"
#include "ADS131M08.h"
#include "ADS131ESP.h"

StreamController *streamController;
ADS131M08 adc;

void setup()
{
  Serial.begin(115200);
  streamController = new StreamController();
  streamController->connect("4GEE-WiFi-5866-2.4GHz", "hWnqeViMi37t");
  //streamController->connect("iPhone", "teo13579");
  adc.begin();
  adc.RESET();
  adc.STANDBY();
  for (int adsIndex = 0; adsIndex < NUM_ADS; adsIndex++)
  {
    adc.writeReg(adsIndex, ADS131_CLOCK, 0b1111111100001110); // Clock register (page 55 in datasheet) 2000
    //adc.writeReg(adsIndex, ADS131_CLOCK, 0b1111111100001010); // Clock register (page 55 in datasheet)
    // /*CLOCK REG SETTINGS
    //  * Bits 15-8: ADC Channel enable/disable
    //  * Bit 7: Crystal disable
    //  * Bit 6: External Reference Enable
    //  * Bit 5: Reserved
    //  * Bits 4-2: Modulator Oversampling 000 = 128 OSR (32ksps), 111 = 16256 OSR (250sps)
    //  * Bits 1-0: Power mode selections 11 or 10 = high resolution, 01 = low power, 00 = very low power
    //  */
    adc.writeReg(adsIndex, ADS131_CFG, 0b0000000000000000);
    // //DC Block Filter settings:
    adc.writeReg(adsIndex, ADS131_THRSHLD_LSB, 0b0000000000000100);
    // //Channel settings
    adc.writeReg(adsIndex, ADS131_CH0_CFG, 0b0000000000000000);
    // //Gain settings, 1-128 (increasing by factor of 2)
  }

  adc.setGain(128);
  adc.WAKEUP();
  delayMicroseconds(50);
  adc.startData();
}

uint8_t maxReading = 0;
void loop()
{
  const unsigned int measurementPeriod_us = 1000000 * NUM_CONVERSIONS_PER_FRAME / SAMPLE_FREQUENCY_HZ
  // const int measurementPeriod_us = 500 * NUM_CONVERSIONS_PER_FRAME;
  static int lastMeasurementTime = micros();
  // if (!adc.frameReady() & (micros() - lastMeasurementTime > measurementPeriod_us))
  // {
  //   Serial.println("Warning");
  // }

  if (adc.frameReady() & (micros() - lastMeasurementTime > measurementPeriod_us))
  {

    lastMeasurementTime = micros();
    streamController->addReading(adc.framePointer(), adc.frameSize());
    adc.newFrame();
  }
  adc.run();


  // uint8_t data[480] = {0};

  // if((micros() - lastMeasurementTime > measurementPeriod_us))
  // {
  //   lastMeasurementTime = micros();
  //   streamController->addReading(&(data[0]), 480);
  // }
}
