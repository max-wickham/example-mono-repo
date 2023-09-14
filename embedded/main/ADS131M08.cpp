
#include "ADS131M08.h"
#include "ADS131ESP.h"


SPIClass ads_spi(ADS131_PORT);


volatile static uint8_t ADS131_dataFrame[NUM_CONVERSIONS_PER_FRAME][DATA_BYTES_PER_CONVERSION];

volatile uint32_t ADS131_statusFrame[NUM_CONVERSIONS_PER_FRAME];
volatile uint32_t ADS131_CRCFrame[NUM_CONVERSIONS_PER_FRAME];
volatile uint8_t index_in_frame;
volatile bool frame_Running = false;
volatile bool frame_Ready = false;
volatile bool frame_Overrun = false;
volatile uint8_t sample_counter = 0;



void ADS131_dataReadyISR(void);



ADS131M08::ADS131M08(void)
{

}

void ADS131M08::begin(void) {

  uint32_t responseArr[10];

    pinMode(ADS131_RESET_PIN, OUTPUT);
    digitalWrite(ADS131_RESET_PIN, HIGH);
    pinMode(ADS131_SSEL_PIN, OUTPUT);
    digitalWrite(ADS131_SSEL_PIN, HIGH);
    pinMode(ADS131_DRDY_PIN, INPUT_PULLUP);
    pinMode(DEBUG_PIN, OUTPUT);
    digitalWrite(DEBUG_PIN, LOW);
    ads_spi.begin(ADS131_SCK_PIN, ADS131_MISO_PIN, ADS131_MOSI_PIN, 0);

    ads_spi.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));

    delay(20); // time for SPI setup
    hw_reset();

    // dummy transfers to clear data buffer
    spiCommFrame(&responseArr[0]);
    spiCommFrame(&responseArr[0]);

    // Attach the ISR
    attachInterrupt(ADS131_DRDY_PIN, ADS131_dataReadyISR, FALLING); // interrupt on each conversion

}

void ADS131M08::hw_reset()  // Hardware Reset"
{
  Serial.println("HW Reset");
  digitalWrite( ADS131_RESET_PIN, LOW);
  delay(ADS131_RESET_PULSE);
  digitalWrite( ADS131_RESET_PIN , HIGH);
  delay(ADS131_RESET_DELAY);
  delay(1); //time for registers to settle 1 ms

}

void ADS131M08::startData(void) // Begin the filling of the data frame with conversions
{
  frame_Ready = false;
  frame_Overrun = false;
  index_in_frame = 0;
  frame_Running = true;
}

void ADS131M08::stopData(void) // Stop the filling of the data frame with conversions
{
  frame_Ready = false;
  frame_Overrun = false;
  index_in_frame = 0;
  frame_Running = false;
}

void ADS131M08::newFrame(void) // reset the data frame
{
  frame_Ready = false;
  frame_Overrun = false;
  index_in_frame = 0;
}

bool ADS131M08::frameReady(void) // return the frame ready flag
{
  return frame_Ready;

}

uint16_t ADS131M08::frameSize(void) // return the size of the data frame
{
  return sizeof(ADS131_dataFrame);
}

uint8_t* ADS131M08::framePointer(void) // return a pointer to the data frame
{
  return (uint8_t*) &ADS131_dataFrame[0][0];
}

 /*
 * Interrupt that gets called when DRDY goes HIGH.
 * Transfers data and sets a flag.
 */
void ADS131_dataReadyISR(void) {
    if(frame_Running && (index_in_frame < NUM_CONVERSIONS_PER_FRAME))
    {
      digitalWrite(ADS131_SSEL_PIN, LOW);
      // get the status data
      ADS131_statusFrame[index_in_frame] = 0;
      ADS131_statusFrame[index_in_frame] |= ads_spi.transfer(0x00) << 16;
      ADS131_statusFrame[index_in_frame] |= ads_spi.transfer(0x00) << 8;
      ADS131_statusFrame[index_in_frame] |= ads_spi.transfer(0x00);
      // add the header byte
      ADS131_dataFrame[index_in_frame][0] = 0xA0;
      // add the sample number
      ADS131_dataFrame[index_in_frame][1] = sample_counter++;
      // channel 1
      ADS131_dataFrame[index_in_frame][2] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][3] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][4] = ads_spi.transfer(0x00);
      // channel 2
      ADS131_dataFrame[index_in_frame][5] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][6] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][7] = ads_spi.transfer(0x00);
      // channel 3
      ADS131_dataFrame[index_in_frame][8] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][9] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][10] = ads_spi.transfer(0x00);
      // channel 4
      ADS131_dataFrame[index_in_frame][11] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][12] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][13] = ads_spi.transfer(0x00);
      // channel 5
      ADS131_dataFrame[index_in_frame][14] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][15] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][16] = ads_spi.transfer(0x00);
      // channel 6
      ADS131_dataFrame[index_in_frame][17] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][18] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][19] = ads_spi.transfer(0x00);
      // channel 7
      ADS131_dataFrame[index_in_frame][20] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][21] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][22] = ads_spi.transfer(0x00);
      // channel 8
      ADS131_dataFrame[index_in_frame][23] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][24] = ads_spi.transfer(0x00);
      ADS131_dataFrame[index_in_frame][25] = ads_spi.transfer(0x00);
      // get CRC
      ADS131_CRCFrame[index_in_frame] = ads_spi.transfer(0x00) << 16;
      ADS131_CRCFrame[index_in_frame] |= ads_spi.transfer(0x00) << 8;
      ADS131_CRCFrame[index_in_frame] |= ads_spi.transfer(0x00);
      //add the footer byte
      ADS131_dataFrame[index_in_frame][32] = 0xC0;

      digitalWrite(ADS131_SSEL_PIN, HIGH);
      index_in_frame++;
      if(index_in_frame == NUM_CONVERSIONS_PER_FRAME) frame_Ready = true;

    }
    else
    {
      frame_Overrun = true;
    }
}



uint16_t ADS131M08::NULL_STATUS(void)
{
  Serial.println("Null Status");
  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(&responseArr[0],ADS131_CMD_NULL );

    // Read response
    spiCommFrame(&responseArr[0]);

    return responseArr[0] >> 16;

}

bool ADS131M08::RESET(void)
{
  Serial.println("SW Reset");
  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(&responseArr[0],ADS131_CMD_RESET );
  delay(1); //time for registers to settle


  // Read response
  spiCommFrame(&responseArr[0]);

  if ((responseArr[0] >> 16) == 0xff28) return true;
  else return false;

}

void ADS131M08::STANDBY(void)
{
  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(&responseArr[0],ADS131_CMD_STANDBY );

  // Read response
  spiCommFrame(&responseArr[0]);


#ifndef ADS131_POLLING
    // Detach the ISR
    detachInterrupt(ADS131_DRDY_PIN);
#endif

  return;
}

void ADS131M08::WAKEUP(void)
{
  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(&responseArr[0],ADS131_CMD_WAKEUP );

  // Read response
  spiCommFrame(&responseArr[0]);

#ifndef ADS131_POLLING
    // Attach the ISR
    attachInterrupt(ADS131_DRDY_PIN, ADS131_dataReadyISR, FALLING);
#endif

  return;
}

void ADS131M08::LOCK(void)
{
  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(&responseArr[0],ADS131_CMD_LOCK );

  // Read response
  spiCommFrame(&responseArr[0]);

  return;
}

void ADS131M08::UNLOCK(void)
{
  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(&responseArr[0],ADS131_CMD_UNLOCK );

  // Read response
  spiCommFrame(&responseArr[0]);

  return;
}



bool ADS131M08::globalChop(bool enabled, uint8_t log2delay) {
    /* Function to configure global chop mode for the ADS131M04.

        INPUTS:
        enabled - Whether to enable global-chop mode.
        log2delay   - Base 2 log of the desired delay in modulator clocks periods
        before measurment begins
        Possible values are between and including 1 and 16, to give delays
        between 2 and 65536 clock periods respectively
        For more information, refer to the datasheet.

        Returns true if settings were written succesfully.
    */

    uint8_t delayRegData = log2delay - 1;

    // Get current settings for current detect mode from the CFG register
    uint16_t currentDetSett = (readReg(ADS131_CFG) << 8) >>8;

    uint16_t newRegData = (delayRegData << 12) + (enabled << 8) + currentDetSett;

    return writeReg(ADS131_CFG, newRegData);
}

bool ADS131M08::writeReg(uint16_t reg, uint16_t data) {
    /* Writes the content of data to the register reg
        Returns true if successful
    */


    // Make command word using syntax found in data sheet
    uint16_t commandWord = ADS131_CMD_WREG + (reg<<7);

    uint32_t responseArr[10];

    // Use first frame to send command
    spiCommFrame(&responseArr[0], commandWord, data);

    // Get response
    spiCommFrame(&responseArr[0]);

    if ( ( (0x04<<12) + (reg<<7) ) == responseArr[0]) {
        return true;
    } else {
        return false;
    }
}

uint16_t ADS131M08::readReg(uint16_t reg) {
    /* Reads the content of single register found at address reg
        Returns register value
    */


    // Make command word using syntax found in data sheet
    uint16_t commandWord = ADS131_CMD_RREG + (reg << 7);

    uint32_t responseArr[10];
    // Use first frame to send command
    spiCommFrame(&responseArr[0], commandWord);

    // Read response
    spiCommFrame(&responseArr[0]);

    return responseArr[0] >> 16;
}

uint32_t ADS131M08::spiTransferWord(uint16_t inputData) {
    /* Transfer 16 bit data as a 24 bit word
      24 bit Data returned is returned as 32 bit MSB aligned
    */


    uint32_t data = ads_spi.transfer(inputData >> 8);
    data <<= 8;
    data |= ads_spi.transfer((inputData<<8) >> 8);
    data <<= 8;
    data |= ads_spi.transfer(0x00);

    return data << 8;
}

void ADS131M08::spiCommFrame(uint32_t * outPtr, uint16_t command, uint16_t data) {
    // Saves all the data of a communication frame to an array with pointer outPtr

    digitalWrite(ADS131_SSEL_PIN, LOW);
    //Serial.print("Send: ");
    //Serial.print(command,HEX);
    //Serial.print(", ");
    //Serial.print(data,HEX);
    //Serial.print(" Receive: ");

    // Send the command in the first word
    *outPtr = spiTransferWord(command);
    //Serial.print(*outPtr,HEX);
    //Serial.print(", ");
    outPtr++;

    // Send the data in the second word if any
    *outPtr = spiTransferWord(data);
    //Serial.print(*outPtr,HEX);
    //Serial.print(", ");
    outPtr++;

    // For the next 7 words, just read the data
    for (uint8_t i=1; i < 8; i++) {

        *outPtr = spiTransferWord() >> 8;
        //Serial.print(*outPtr,HEX);
        //Serial.print(", ");
        outPtr++;
    }


    // Save CRC bits
    *outPtr = spiTransferWord();
    //Serial.print(*outPtr,HEX);
    //Serial.println(";  ");

    digitalWrite(ADS131_SSEL_PIN, HIGH);
}



bool ADS131M08::setGain(int gain) { // apply gain to all channels (1 to 128, base 2 (1,2,4,8,16,32,64,128))
    uint16_t writegain = 0;
    if(gain == 1 ) {
        writegain = 0b0000000000000000;
    }
    else if (gain == 2) {
        writegain = 0b0001000100010001;
    }
    else if (gain == 4) {
        writegain = 0b0010001000100010;
    }
    else if (gain == 8) {
        writegain = 0b0011001100110011;
    }
    else if (gain == 16) {
        writegain = 0b0100010001000100;
    }
    else if (gain == 32) {
        writegain = 0b0101010101010101;
    }
    else if (gain == 64) {
        writegain = 0b0110011001100110;
    }
    else if (gain == 128) {
        writegain = 0b0111011101110111;
    }
    else {
        return false;
    }
    writeReg(ADS131_GAIN1, writegain);
    writeReg(ADS131_GAIN2, writegain);

    return true;
}
