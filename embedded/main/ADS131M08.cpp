
#include "ADS131M08.h"
#include "ADS131ESP.h"

#define loop_ads for (int adsIndex=0; adsIndex < NUM_ADS; adsIndex++)

SPIClass ads_spi(ADS131_PORT);

volatile static uint8_t ADS131_dataFrame[NUM_CONVERSIONS_PER_FRAME][DATA_BYTES_PER_CONVERSION];

volatile uint32_t ADS131_statusFrame[NUM_ADS][NUM_CONVERSIONS_PER_FRAME];
volatile uint32_t ADS131_CRCFrame[NUM_ADS][NUM_CONVERSIONS_PER_FRAME];
volatile uint8_t index_in_frame;
volatile bool frame_Running = false;
volatile bool frame_Ready = false;
volatile bool frame_Overrun = false;
volatile uint8_t sample_counter = 0;

volatile bool receivedFrame[NUM_ADS] = {false};

const int selectPins[NUM_ADS] = ADS131_SELECT_PINS;
const int resetPins[NUM_ADS] = ADS131_RESET_PINS;
const int drdyPins[NUM_ADS] = ADS131_DRDY_PINS;

void enADS(int adsIndex)
{
  digitalWrite(selectPins[adsIndex], LOW);
}

void disADS(int adsIndex)
{
  digitalWrite(selectPins[adsIndex], HIGH);
}

void enAllADS()
{
  loop_ads
  {
    digitalWrite(selectPins[adsIndex], LOW);
  }
}
void disAllADS()
{
  loop_ads
  {
    digitalWrite(selectPins[adsIndex], HIGH);
  }
}

template <int adsCallbackIndex>
void ADS131_dataReadyISR(void);

// !!!! Careful Super hacky way to do this

template <int adsIndex>
void setADSCallbacks()
{
  attachInterrupt(drdyPins[adsIndex], ADS131_dataReadyISR<adsIndex>, FALLING); // interrupt on
  setADSCallbacks<adsIndex - 1>();
}
template <>
void setADSCallbacks<0>()
{
  attachInterrupt(drdyPins[0], ADS131_dataReadyISR<0>, FALLING); // interrupt on
}

void ADS131M08::begin(void)
{

  uint32_t responseArr[10];

  loop_ads
  {
    pinMode(resetPins[adsIndex], OUTPUT);
    digitalWrite(resetPins[adsIndex], HIGH);
    pinMode(selectPins[adsIndex], OUTPUT);
    digitalWrite(selectPins[adsIndex], HIGH);
    pinMode(drdyPins[adsIndex], INPUT_PULLUP);
  }
  pinMode(DEBUG_PIN, OUTPUT);
  digitalWrite(DEBUG_PIN, LOW);

  ads_spi.begin(ADS131_SCK_PIN, ADS131_MISO_PIN, ADS131_MOSI_PIN, 0);

  ads_spi.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));

  delay(20); // time for SPI setup
  hw_reset();

  // dummy transfers to clear data buffer
  loop_ads
  {
    spiCommFrame(adsIndex, &responseArr[0]);
    spiCommFrame(adsIndex, &responseArr[0]);
  }

  // Attach the ISR
  setADSCallbacks<NUM_ADS>();
  // loop_ads
  // {
  //   attachInterrupt(drdyPins[adsIndex], ADS131_dataReadyISR<adsIndex>, FALLING); // interrupt on each conversion
  // }
}

void ADS131M08::hw_reset() // Hardware Reset"
{
  loop_ads
  {
    Serial.println("HW Reset");
    digitalWrite(resetPins[adsIndex], LOW);
    delay(ADS131_RESET_PULSE);
    digitalWrite(resetPins[adsIndex], HIGH);
    delay(ADS131_RESET_DELAY);
    delay(1); // time for registers to settle 1 ms
  }
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

uint8_t *ADS131M08::framePointer(void) // return a pointer to the data frame
{
  return (uint8_t *)&ADS131_dataFrame[0][0];
}

/*
 * Interrupt that gets called when DRDY goes HIGH.
 * Transfers data and sets a flag.
 */
template <int adsCallbackIndex>
void ADS131_dataReadyISR(void)
{
#ifdef OPEN_BCI
  const int header_offset = 2;
#else
  const int header_offset = 0;
#endif

  Serial.println("Interrupt Triggered");

  receivedFrame[adsCallbackIndex] == true;

  if (frame_Running && (index_in_frame < NUM_CONVERSIONS_PER_FRAME))
  {
    Serial.println("Saving Frame");
    Serial.println(index_in_frame);
    disAllADS();
    enADS(adsCallbackIndex);

    // get the status data
    ADS131_statusFrame[adsCallbackIndex][index_in_frame] = 0;
    ADS131_statusFrame[adsCallbackIndex][index_in_frame] |= ads_spi.transfer(0x00) << 16;
    ADS131_statusFrame[adsCallbackIndex][index_in_frame] |= ads_spi.transfer(0x00) << 8;
    ADS131_statusFrame[adsCallbackIndex][index_in_frame] |= ads_spi.transfer(0x00);

    // get the frame data
    for (int index = adsCallbackIndex * NUM_CHANNELS_PER_ADS * 3;
         index < NUM_CHANNELS_PER_ADS * 3 + adsCallbackIndex * NUM_CHANNELS_PER_ADS * 3;
         index++)
    {
      ADS131_dataFrame[index_in_frame][header_offset + index] = ads_spi.transfer(0x00);
    }

    // get CRC
    ADS131_CRCFrame[adsCallbackIndex][index_in_frame] = ads_spi.transfer(0x00) << 16;
    ADS131_CRCFrame[adsCallbackIndex][index_in_frame] |= ads_spi.transfer(0x00) << 8;
    ADS131_CRCFrame[adsCallbackIndex][index_in_frame] |= ads_spi.transfer(0x00);

    disADS(adsCallbackIndex);

    bool allFramesReceived = true;
    loop_ads
    {
      allFramesReceived = allFramesReceived & receivedFrame[adsIndex];
    }
    if (allFramesReceived)
    {
      // Set header and footer if needed
#ifdef OPEN_BCI
      // add the header byte
      ADS131_dataFrame[index_in_frame][0] = 0xA0;
      // add the sample number
      ADS131_dataFrame[index_in_frame][1] = sample_counter++;
      // add the footer byte
      ADS131_dataFrame[index_in_frame][8 + NUM_ADS * NUM_CHANNELS_PER_ADS * 3] = 0xC0;
#endif
      loop_ads
      {
        receivedFrame[adsIndex] = false;
      }
      index_in_frame++;
    }

    if (index_in_frame == NUM_CONVERSIONS_PER_FRAME)
    {
      frame_Ready = true;
    }
  }
  else
  {
    frame_Overrun = true;
  }
}

uint16_t ADS131M08::NULL_STATUS(int adsIndex)
{
  Serial.println("Null Status");
  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(adsIndex, &responseArr[0], ADS131_CMD_NULL);

  // Read response
  spiCommFrame(adsIndex, &responseArr[0]);

  return responseArr[0] >> 16;
}

bool ADS131M08::RESET()
{
  loop_ads
  {
    Serial.println("SW Reset");
    uint32_t responseArr[10];
    // Use first frame to send command
    spiCommFrame(adsIndex, &responseArr[0], ADS131_CMD_RESET);
    delay(1); // time for registers to settle

    // Read response
    spiCommFrame(adsIndex, &responseArr[0]);

    if ((responseArr[0] >> 16) == 0xff28)
      return true;
    else
      return false;
  }
}

void ADS131M08::STANDBY()
{
  loop_ads
  {
    uint32_t responseArr[10];
    // Use first frame to send command
    spiCommFrame(adsIndex, &responseArr[0], ADS131_CMD_STANDBY);

    // Read response
    spiCommFrame(adsIndex, &responseArr[0]);

#ifndef ADS131_POLLING
    // Detach the ISR
    loop_ads
    {
      detachInterrupt(drdyPins[adsIndex]);
    }
#endif
  }
  return;
}

void ADS131M08::WAKEUP()
{
  loop_ads
  {
    uint32_t responseArr[10];
    // Use first frame to send command
    spiCommFrame(adsIndex, &responseArr[0], ADS131_CMD_WAKEUP);

    // Read response
    spiCommFrame(adsIndex, &responseArr[0]);

#ifndef ADS131_POLLING
    // Attach the ISR
    setADSCallbacks<NUM_ADS>();
#endif
  }
  return;
}

void ADS131M08::LOCK()
{
  loop_ads
  {
    uint32_t responseArr[10];
    // Use first frame to send command
    spiCommFrame(adsIndex, &responseArr[0], ADS131_CMD_LOCK);

    // Read response
    spiCommFrame(adsIndex, &responseArr[0]);
  }
  return;
}

void ADS131M08::UNLOCK()
{
  loop_ads
  {
    uint32_t responseArr[10];
    // Use first frame to send command
    spiCommFrame(adsIndex, &responseArr[0], ADS131_CMD_UNLOCK);

    // Read response
    spiCommFrame(adsIndex, &responseArr[0]);
  }

  return;
}

bool ADS131M08::globalChop(int adsIndex, bool enabled, uint8_t log2delay)
{
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
  uint16_t currentDetSett = (readReg(adsIndex, ADS131_CFG) << 8) >> 8;

  uint16_t newRegData = (delayRegData << 12) + (enabled << 8) + currentDetSett;

  return writeReg(adsIndex, ADS131_CFG, newRegData);
}

bool ADS131M08::writeReg(int adsIndex, uint16_t reg, uint16_t data)
{
  bool result = true;
  for (int ads_index = 0; ads_index < NUM_ADS; ads_index++)
  {
    /* Writes the content of data to the register reg
        Returns true if successful
    */

    // Make command word using syntax found in data sheet
    uint16_t commandWord = ADS131_CMD_WREG + (reg << 7);

    uint32_t responseArr[10];

    // Use first frame to send command
    spiCommFrame(ads_index, &responseArr[0], commandWord, data);

    // Get response
    spiCommFrame(ads_index, &responseArr[0]);

    if (!(((0x04 << 12) + (reg << 7)) == responseArr[0]))
    {
      result = false;
    }
  }
  return result;
}

uint16_t ADS131M08::readReg(int adsIndex, uint16_t reg)
{
  /* Reads the content of single register found at address reg
      Returns register value
  */

  // Make command word using syntax found in data sheet
  uint16_t commandWord = ADS131_CMD_RREG + (reg << 7);

  uint32_t responseArr[10];
  // Use first frame to send command
  spiCommFrame(adsIndex, &responseArr[0], commandWord);

  // Read response
  spiCommFrame(adsIndex, &responseArr[0]);

  return responseArr[0] >> 16;
}

uint32_t ADS131M08::spiTransferWord(uint16_t inputData)
{
  /* Transfer 16 bit data as a 24 bit word
    24 bit Data returned is returned as 32 bit MSB aligned
  */

  uint32_t data = ads_spi.transfer(inputData >> 8);
  data <<= 8;
  data |= ads_spi.transfer((inputData << 8) >> 8);
  data <<= 8;
  data |= ads_spi.transfer(0x00);

  return data << 8;
}

void ADS131M08::spiCommFrame(int adsIndex, uint32_t *outPtr, uint16_t command, uint16_t data)
{
  // Saves all the data of a communication frame to an array with pointer outPtr
  enADS(adsIndex);
  // Serial.print("Send: ");
  // Serial.print(command,HEX);
  // Serial.print(", ");
  // Serial.print(data,HEX);
  // Serial.print(" Receive: ");

  // Send the command in the first word
  *outPtr = spiTransferWord(command);
  // Serial.print(*outPtr,HEX);
  // Serial.print(", ");
  outPtr++;

  // Send the data in the second word if any
  *outPtr = spiTransferWord(data);
  // Serial.print(*outPtr,HEX);
  // Serial.print(", ");
  outPtr++;

  // For the next 7 words, just read the data
  for (uint8_t i = 1; i < 8; i++)
  {

    *outPtr = spiTransferWord() >> 8;
    // Serial.print(*outPtr,HEX);
    // Serial.print(", ");
    outPtr++;
  }

  // Save CRC bits
  *outPtr = spiTransferWord();
  // Serial.print(*outPtr,HEX);
  // Serial.println(";  ");
  disADS(adsIndex);
}

bool ADS131M08::setGain(int gain)
{ // apply gain to all channels (1 to 128, base 2 (1,2,4,8,16,32,64,128))
  uint16_t writegain = 0;
  if (gain == 1)
  {
    writegain = 0b0000000000000000;
  }
  else if (gain == 2)
  {
    writegain = 0b0001000100010001;
  }
  else if (gain == 4)
  {
    writegain = 0b0010001000100010;
  }
  else if (gain == 8)
  {
    writegain = 0b0011001100110011;
  }
  else if (gain == 16)
  {
    writegain = 0b0100010001000100;
  }
  else if (gain == 32)
  {
    writegain = 0b0101010101010101;
  }
  else if (gain == 64)
  {
    writegain = 0b0110011001100110;
  }
  else if (gain == 128)
  {
    writegain = 0b0111011101110111;
  }
  else
  {
    return false;
  }
  loop_ads
  {
    writeReg(adsIndex, ADS131_GAIN1, writegain);
    writeReg(adsIndex, ADS131_GAIN2, writegain);
  }

  return true;
}
