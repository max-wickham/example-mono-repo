#include <string>
#include <cstring>
#include <WiFi.h>
#include <atomic>
#include <memory>
// #include <HTTPClient.h>
#include "esp_private/wifi.h"
#include "esp_wifi.h"
#include <WiFiUdp.h>
#include "ADS131M08.h"

// #include <WebServer.h> // WebServer Library for ESP32
// #include <WebSocketsClient.h>

#define FRAME_SIZE (NUM_CHANNELS_PER_ADS * NUM_BYTES_PER_INT * NUM_CONVERSIONS_PER_FRAME * NUM_ADS)
#define MAX_READINGS FRAME_SIZE * 3

const std::string serverAddress = "138.68.161.150";
const int serverPort = 8005;
const std::string route = "/sample/";
// const char* test_message = "test message";
uint8_t readingBuffer1[MAX_READINGS] = {0};
uint8_t readingBuffer2[MAX_READINGS] = {0};

WiFiUDP udp;
int sessionID = 12;
class StreamController
{
    // WebSocketsClient webSocket; // websocket client class instance

    int readingIndex = 0;

    TaskHandle_t task;

    std::atomic<bool> streaming;
    std::atomic<bool> writing;

    bool running = true;

    uint8_t *writingBuffer = &(readingBuffer1[0]);
    uint8_t *streamingBuffer = &(readingBuffer2[0]);

    static void sendReadings(void *pvParameters)
    {
        StreamController *l_this = (StreamController *)pvParameters;
        while (l_this->running)
        {
            if (l_this->streaming)
            {
                // WiFiClient client;
                // HTTPClient http;
                // http.begin(client,  "http://165.22.123.190:8005/sample/12");
                // http.addHeader("Content-Type", "application/octet-stream");
                // int httpResponseCode = http.POST(l_this->streamingBuffer, MAX_READINGS);
                // Serial.println(httpResponseCode);
                // http.end();
                // uint8_t streamID[4] = {0x00, 0x00, 0x00, 0x0D};
                udp.beginPacket(serverAddress.c_str(), 8888);
                // Send the header packets
                udp.write(0xAA);
                // udp.write(&(streamID[0]), 4);
                udp.write((uint8_t *)(&sessionID), 4);
                // Send the data
                udp.write(l_this->streamingBuffer,MAX_READINGS);
                udp.endPacket();
                // l_this->webSocket.sendBIN(l_this->streamingBuffer, MAX_READINGS);
            }
            l_this->streaming = false;
            if (l_this->writing){
              Serial.println("Start Waiting for writing");
            }
            while (l_this->writing)
            {
            }
            l_this->streamingBuffer = l_this->streamingBuffer == readingBuffer1 ? readingBuffer2 : readingBuffer1;
            l_this->writing = true;
            while (!l_this->streaming)
            {
            }
        }
    }

public:

    StreamController(){
        streaming = false;
        writing = true;
    }
    void
    connect(std::string ssid, std::string password)
    {
        // TODO should generate a random session ID

        WiFi.mode(WIFI_STA); // Optional
        // esp_wifi_config_80211_tx_rate(WIFI_IF_STA, WIFI_PHY_RATE_11M_S);
        Serial.println(esp_wifi_internal_set_fix_rate(WIFI_IF_STA, true, WIFI_PHY_RATE_11M_S));
        WiFi.begin(ssid.c_str(), password.c_str());
        Serial.println("\nConnecting");

        while (WiFi.status() != WL_CONNECTED)
        {
            Serial.print(".");
            delay(100);
        }

        Serial.println("\nConnected to the WiFi network");
        Serial.print("Local ESP32 IP: ");
        Serial.println(WiFi.localIP());
        // webSocket.begin(serverAddress.c_str(), serverPort, (route + std::to_string(sessionID)).c_str());


        // String serverName = "http://www.google.com";
        // HTTPClient http;
        // http.begin(serverName.c_str());
        // int httpResponseCode = http.GET();
        // Serial.println(httpResponseCode);

        Serial.println("\nConnecting Websocket");
        // while (!webSocket.isConnected()){
        //    Serial.print(".");
        //     delay(100);
        // }
        // webSocket.setReconnectInterval(5000);

        xTaskCreatePinnedToCore(
            sendReadings, /* Task function. */
            "Task1",      /* name of task. */
            10000,        /* Stack size of task */
            this,         /* parameter of the task */
            1,            /* priority of the task */
            &task,        /* Task handle to keep track of created task */
            1);           /* pin task to core 1 */
    }

    void addReading(int32_t &reading){
        unsigned char *bytePtr = reinterpret_cast<unsigned char *>(&reading);
        addReading(bytePtr, 4);
    }

    void addReading(uint8_t* framePointer, size_t frameLength)
    {
        if (readingIndex == 0){
            Serial.println("Start of buffer");
        }
        // unsigned char *bytePtr = reinterpret_cast<unsigned char *>(&framePointer);
        //
        for (int i = 0; i < frameLength; i++)
        {
            writingBuffer[i + readingIndex] = framePointer[i];
        }
        readingIndex += frameLength;
        if (readingIndex == MAX_READINGS)
        {
            // Serial.println("End of buffer");
            readingIndex = 0;
            this->writing = false;
            // Serial.println("Set to false");
            if (this->streaming){
              Serial.println("waiting for streaming");
            }
            while (this->streaming)
            {
            }
            // Serial.println("End of streaming");
            writingBuffer = writingBuffer == readingBuffer1 ? readingBuffer2 : readingBuffer1;
            this->streaming = true;
            while (!this->writing)
            {
            }
            // Serial.println("End of waiting");
        }
    }


    void run()
    {
        // webSocket.loop();
    }

    bool isConnected()
    {
    }

    int getID()
    {
    }
};
