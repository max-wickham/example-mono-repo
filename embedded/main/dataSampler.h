struct DataPacket {
  byte packet[16];
  int32_t sampleTime;
};


class DataSampler {
  private:
  const static int NUM_SAMPLES = 100;
  DataPacket recordedData[NUM_SAMPLES];
  bool isRecordingState = false;
  int recordingIndex = 0;

  private:
  void record() {
    if (recordingIndex >= NUM_SAMPLES) {
      stopRecording();
    }
  }

  public:

  bool isRecording() {
    // return true if currently recording data
    return isRecordingState;
  }

  void startRecording() {
    // start recording data (clearing old data)
    recordingIndex = 0;
    isRecordingState = true;
  }

  void stopRecording() {
    // stop data recording
    isRecordingState = false;
  }

  DataPacket currentData() {
    // Return the current data reading
  }

  void setup() {

  }

  void run() {

    if (isRecordingState) {
      // TODO record
      record();
    }


  }

};
