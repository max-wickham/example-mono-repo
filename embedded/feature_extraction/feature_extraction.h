// feature_extraction.h

// Containing all the functions to extract features in C++

#pragma once
#include <vector>

double rms(const float input_emg[], int length);
double mav(const float input_emg[], int length);
double median_av(const float input_emg[], int length);
double iemg(const float input_emg[], int length);
double variance(const float input_emg[], int length);
double std_dev(const float input_emg[], int length);
int zero_crossing(const float input_emg[], int length);
double waveform_length(const float input_emg[], int length);
int slope_sign_changes(const float input_emg[], int length);
double skewness(const float input_emg[], int length, bool bias = false);
