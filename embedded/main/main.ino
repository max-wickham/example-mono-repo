#include "streamController.h"

StreamController *streamController;

void setup()
{
  Serial.begin(115200);
  streamController = new StreamController();
  streamController->connect("Billacombe", "browntrout");
}

void loop()
{
  static unsigned long lastTime = micros();
  static float reading = 0;
  streamController->run();
  if (micros() - lastTime > 500ul)
  {
    reading += 0.01f;
    lastTime = micros();
    for (int i = 0; i < 16; i++)
    {
      streamController->addReading(reading);
    }
  }
}
