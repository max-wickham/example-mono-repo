
// feature_extraction.cpp
#include "feature_extraction.h"
#include <cmath>
#include <algorithm>
#include <numeric>


// TIME DOMAIN FEATURES


double rms(const float input_emg[], int length) {
    double sum = 0.0;
    for (int i = 0; i < length; i++) {
        sum += input_emg[i] * input_emg[i];
    }
    return sqrt(sum / length);
}


double mav(const float input_emg[], int length) {
    double sum = 0.0;
    for (int i = 0; i < length; i++) {
        sum += fabs(input_emg[i]); // Use fabs for floating-point numbers
    }
    return sum / length;
}

double median_av(const float input_emg[], int length) {
    float abs_values[length];
    for(int i = 0; i < length; i++) {
        abs_values[i] = fabs(input_emg[i]);
    }
    std::sort(abs_values, abs_values + length);
    if (length % 2 == 0) {
        return (abs_values[length/2 - 1] + abs_values[length/2]) / 2.0;
    } else {
        return abs_values[length/2];
    }
}


double iemg(const float input_emg[], int length) {
    return mav(input_emg, length) * length;
}


double variance(const float input_emg[], int length) {
    double mean = mav(input_emg, length);
    double sum = 0.0;
    for (int i = 0; i < length; i++) {
        double diff = input_emg[i] - mean;
        sum += diff * diff;
    }
    return sum / length;
}

double std_dev(const float input_emg[], int length) {
    return sqrt(variance(input_emg, length));
}

int zero_crossing(const float input_emg[], int length) {
    int count = 0;
    for (int i = 0; i < length - 1; i++) {
        if (input_emg[i] * input_emg[i + 1] < 0) count++;
    }
    return count;
}

double waveform_length(const float input_emg[], int length) {
    double sum = 0.0;
    for (int i = 0; i < length - 1; i++) {
        sum += fabs(input_emg[i + 1] - input_emg[i]);
    }
    return sum;
}


int slope_sign_changes(const float input_emg[], int length) {
    int count = 0;
    for (int i = 1; i < length - 1; i++) {
        if ((input_emg[i - 1] - input_emg[i]) * (input_emg[i] - input_emg[i + 1]) < 0) count++;
    }
    return count;
}

double skewness(const float input_emg[], int length, bool bias) {
    double sum = 0.0;
    for(int i = 0; i < length; i++) {
        sum += input_emg[i];
    }
    double mean = sum / length;
    double m3 = 0.0; // Third central moment
    double m2 = 0.0; // Second central moment (variance)
    
    for (int i = 0; i < length; i++) {
        double diff = input_emg[i] - mean;
        m3 += std::pow(diff, 3);
        m2 += std::pow(diff, 2);
    }
    
    m3 /= length; // Biased third central moment
    m2 /= length; // Biased second central moment (variance)

    double skewness;
    if (bias) {
        skewness = m3 / std::pow(m2, 1.5);
    } else {
        // Adjusted Fisher-Pearson standardized moment coefficient
        int n = length;
        skewness = std::sqrt(n * (n - 1)) / (n - 2) * m3 / std::pow(m2, 1.5);
    }

    return skewness;
}


// FREQUENCY DOMAIN FEATURES

// to do write the spectrogram and periodogram functions