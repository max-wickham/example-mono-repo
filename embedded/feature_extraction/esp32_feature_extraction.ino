
#include "feature_extraction.h"

#define NUM_CHANNELS 8
#define NUM_SAMPLES 1000
#define NUM_FEATURES 10

float emg_data[NUM_CHANNELS][NUM_SAMPLES];

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  readAnalogEMG();
  float feature_matrix[NUM_FEATURES][NUM_CHANNELS];

   for (int channel = 0; channel < NUM_CHANNELS; channel++) {
    feature_matrix[0][channel] = rms(emg_data[channel], NUM_SAMPLES);
    feature_matrix[1][channel] = mav(emg_data[channel], NUM_SAMPLES);
    feature_matrix[2][channel] = median_av(emg_data[channel], NUM_SAMPLES);
    feature_matrix[3][channel] = iemg(emg_data[channel], NUM_SAMPLES);
    feature_matrix[4][channel] = variance(emg_data[channel], NUM_SAMPLES);
    feature_matrix[5][channel] = std_dev(emg_data[channel], NUM_SAMPLES);
    feature_matrix[6][channel] = zero_crossing(emg_data[channel], NUM_SAMPLES);
    feature_matrix[7][channel] = waveform_length(emg_data[channel], NUM_SAMPLES);
    feature_matrix[8][channel] = slope_sign_changes(emg_data[channel], NUM_SAMPLES);
    feature_matrix[9][channel] = skewness(emg_data[channel], NUM_SAMPLES);
  }

  // Printing the result matrix
  for (int feature = 0; feature < NUM_FEATURES; feature++) {
    String feature_row = "";
    for (int channel = 0; channel < NUM_CHANNELS; channel++) {
      feature_row += String(feature_matrix[feature][channel]) + "\t";
    }
    Serial.println(feature_row);
  }

  delay(100);

}

void readAnalogEMG() {
  for (int i =0; i < NUM_SAMPLES; i++) {
    for (int channel = 0; channel< NUM_CHANNELS; channel++) {
      emg_data[channel][i] = analogRead(channel);
    }
    delay(1);
  }
}