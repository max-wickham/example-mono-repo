#ifndef Data_Manager
#define Data_Manager

#include <cstring>

struct ReadingPacket {
    float channel[16];
    int32_t sampleTime;
};


const int downloadPacketSize = 400;
// 1khz for 1 second gives 1000 readings
const int maxReadings = 1000;
// 1Kbytes
const int featureDataSizeBytes = 10000;

char featureData[featureDataSizeBytes];
int readIndex = 0;

class DataManager {
    private:
    // TODO set to the correct number (number of windows to download)
    char data[sizeof(ReadingPacket) * maxReadings];

    int writeIndex = 0;
    public:

    DataManager(){
        for(int i = 0; i < featureDataSizeBytes; i++){
            featureData[i] = i;
        }
    }

    // Fill with fake data

    void addPacket(ReadingPacket &packet) {
        // write an individual reading
        std::memcpy(data + writeIndex, &packet, sizeof(ReadingPacket));
        writeIndex += sizeof(ReadingPacket);
    }

    void clearRecording(){
        writeIndex = 0;
    }


    void clearDownload(){
        Serial.println("featureDataSizeBytes");
        Serial.println(featureDataSizeBytes);
        readIndex = 0;
        Serial.println(readIndex);
    }

    bool downloadComplete(){
        return (readIndex >= featureDataSizeBytes);
    }

    void doFeatureExtraction() {
        // TODO implement feature extraction
        // Should store the feature extracted data in featureData
    }

    char* readNextDownloadPacket(){
        Serial.println(readIndex);
        Serial.println("Num readings");
        Serial.println(readIndex);
        Serial.println(featureData);
        Serial.println(&(featureData[0]));
        char* response = &(featureData[0]) + readIndex;
        Serial.println(readIndex);
        readIndex += downloadPacketSize;
        Serial.println(readIndex);
        return response;
    }

    int getRecordingHash(){
        int hash = 0;
        for (int i = 0; i < 1000; i++){
            hash += featureData[featureDataSizeBytes];
        }
        return hash;
    }
};

#endif
