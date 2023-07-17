

struct ReadingPacket {
    float channel[16];
    int32_t sampleTime;
};


const windowSize = 20;
struct DownloadPacket {
    char bytes[200];
}

class DataManager {
    private:
    static const windowsSize = size_t(ReadingPacket);

    // TODO set to the correct number (number of windows to download)
    const numReadPackets = 100;
    // 32kbytes
    char data[32000];
    // 1kbytes
    char featureData[1000];
    int writeIndex = 0;
    int readIndex = 0;

    public:

    void addPacket(ReadingPacket packet) {
        // write an individual reading
        data[writeIndex] = packet
        writeIndex += windowsSize;
    }

    void clearRecording(){
        writeIndex = 0;
    }


    void clearDownload(){
        readIndex = 0;
    }

    bool downloadComplete(){
        return readIndex < numReadPackets;
    }

    void doFeatureExtraction() {
        // TODO implement feature extraction
        // Should store the feature extracted data in featureData
    }

    DownloadPacket readNextDownloadPacket(){
        DownloadPacket packet = featureData[readIndex]
        readIndex += windowsSize;
        return packet;
    }
};
