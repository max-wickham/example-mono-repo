'''Feature Extraction'''
import numpy as np
from scipy import signal
from scipy.stats import skew
from sklearn.preprocessing import StandardScaler




import app.api.routes.functions

# MEAN ABSOLUTE VALUE
def mav(input_emg):
    mav = np.mean(np.abs(input_emg), axis=-1)
    return mav

def median_av(input_emg):
    mav = np.median(np.abs(input_emg), axis=-1)
    return mav

# RMS
def rms(segmented_data):
    rms = np.sqrt(np.mean((segmented_data)** 2, axis=-1))
    return rms

# INTEGRATED EMG
def iemg(input_emg):
    iemg = np.sum(np.abs(input_emg), axis=-1)
    return iemg

# VARIANCE
def variance(input_emg):
    var = np.var(input_emg, axis=-1)
    return var

# STD DEVIATION
def std_dev(input_emg):
    std_dev = np.sqrt(variance(input_emg))
    return std_dev

# ZERO CROSSING
def zero_crossing(input_emg):
    product = input_emg[:, :, :-1] * input_emg[:, :, :-1]
    zc = np.sum(product < 0, axis=-1)
    return zc

# WAVEFORM LENGTH
def waveform_length(input_emg):
    differential = np.diff(input_emg, axis=-1)
    wf_len = np.sum(differential, axis=-1)
    return wf_len

# SLOPE-SIGN CHANGE
def slope_sign_change(input_emg):
    differential = np.diff(input_emg, axis=-1)
    product = differential[:, :, :-1] * differential[:, :, :-1]
    sign_change_count = np.sum(product < 0, axis=-1)

    return sign_change_count
def skewness(input_emg):
    skew_emg = skew(input_emg, axis=-1, bias=False)
    return skew_emg

# NB: FREQUENCY-FEATURES
def spectrogram(emg, fs):
    f, t, Sxx = signal.spectrogram(emg, fs, axis=-1)
    return f, t, Sxx

def periodogram(emg, fs):
    frequencies, periodogram = signal.periodogram(emg, fs, axis=-1, nfft=20)
    return frequencies, periodogram
#---------------------------

def extract_all_features(emg, fs, n_components):

    if emg.ndim == 2:
        emg = functions.segmentation(emg)

    feature_list = ['mav_', 'med_av_', 'rms_', 'iemg_', 'std_', 'var_', 'wfl_', 'ssc_', 'zc_', 'skewness_', 'mav_freq', 'med_av_freq', 'rms_freq', 'iemg_freq', 'std_freq', 'var_freq', 'wfl_freq', 'skewness_freq']

    # time-based features
    mav_ = mav(emg)
    med_av_ = median_av(emg)
    rms_ = rms(emg)
    iemg_ = iemg(emg)
    std_ = std_dev(emg)
    var_ = variance(emg)
    wfl_ = waveform_length(emg)
    ssc_ = slope_sign_change(emg)
    zc_ = zero_crossing(emg)
    skewness_ = skewness(emg)

    # frequency-based features
    #f, t, Sxx = spectrogram(emg, fs)
    f, Pxx = periodogram(emg, fs)

    mav_freq = mav(Pxx)
    med_av_freq = median_av(Pxx)
    rms_freq = rms(Pxx)
    iemg_freq = iemg(Pxx)
    std_freq = std_dev(Pxx)
    var_freq = variance(Pxx)
    wfl_freq = waveform_length(Pxx)
    skewness_freq = skewness(Pxx)

    # stack features
    feature_matrix = np.stack((mav_, med_av_, rms_, iemg_, std_, var_, wfl_, ssc_, zc_, skewness_, mav_freq, med_av_freq, rms_freq, iemg_freq , std_freq, var_freq, wfl_freq, skewness_freq), axis=2)

    #nb DATA RESHAPING
    # given feature_matrix [N, M, T], the reshaped matrix will be [N, TTTTTTT...(M times)]
    # in other words: all features first channel, all features second channel, all features third channel......
    feature_matrix = feature_matrix.reshape(feature_matrix.shape[0], -1)
    feature_matrix_Pxx = Pxx.reshape(Pxx.shape[0], -1)

    # nb DATA STANDARDIZATION
    scaler = StandardScaler()
    scaler.fit(feature_matrix)
    feature_matrix = scaler.transform(feature_matrix)

    scaler_Pxx = StandardScaler()
    scaler_Pxx.fit(feature_matrix_Pxx)
    feature_matrix_Pxx = scaler_Pxx.transform(feature_matrix_Pxx)

    #nb PCA
    feature_matrix_reduced = functions.pca(feature_matrix, n_components)


    return feature_matrix_reduced, feature_matrix_Pxx, feature_list


#def rel_time_feature_extraction(emg, fs, n_components):
def real_time_feature_extraction(emg):
    #feature_list = ['mav_', 'med_av_', 'rms_', 'iemg_', 'std_', 'var_', 'wfl_', 'ssc_', 'zc_', 'skewness_', 'mav_freq', 'med_av_freq', 'rms_freq', 'iemg_freq', 'std_freq', 'var_freq', 'wfl_freq', 'skewness_freq']

    #emg = np.swapaxes(emg, 0, 1)

    # time-based features
    mav_ = mav(emg)
    med_av_ = median_av(emg)
    rms_ = rms(emg)
    iemg_ = iemg(emg)
    ssc_ = slope_sign_change(emg)
    zc_ = zero_crossing(emg)
    wfl_ = waveform_length(emg)
    var_ = variance(emg)

    """std_ = std_dev(emg)
    skewness_ = skewness(emg)

    # frequency-based features
    #f, t, Sxx = spectrogram(emg, fs)
    f, Pxx = periodogram(emg, fs)

    mav_freq = mav(Pxx)
    med_av_freq = median_av(Pxx)
    rms_freq = rms(Pxx)
    iemg_freq = iemg(Pxx)
    std_freq = std_dev(Pxx)
    var_freq = variance(Pxx)
    wfl_freq = waveform_length(Pxx)
    skewness_freq = skewness(Pxx)"""

    # stack features
    #feature_matrix = np.concatenate((mav_, med_av_, rms_, iemg_, ssc_, zc_,  var_, wfl_), axis=0)
    feature_matrix = np.stack((mav_, med_av_, rms_, iemg_, ssc_, zc_, var_, wfl_), axis=2)
    #feature_matrix = np.stack((mav_, med_av_, rms_, iemg_, std_, var_, wfl_, ssc_, zc_, skewness_, mav_freq, med_av_freq, rms_freq, iemg_freq , std_freq, var_freq, wfl_freq, skewness_freq), axis=2)

    #nb DATA RESHAPING
    # given feature_matrix [N, M, T], the reshaped matrix will be [N, TTTTTTT...(M times)]
    # in other words: all features first channel, all features second channel, all features third channel......
    feature_matrix = feature_matrix.reshape(feature_matrix.shape[0], -1)
    #feature_matrix_Pxx = Pxx.reshape(Pxx.shape[0], -1)

    # nb DATA STANDARDIZATION
    # apply after training
    scaler = StandardScaler()
    scaler.fit(feature_matrix)
    feature_matrix = scaler.transform(feature_matrix)

    """scaler_Pxx = StandardScaler()
    scaler_Pxx.fit(feature_matrix_Pxx)
    feature_matrix_Pxx = scaler_Pxx.transform(feature_matrix_Pxx)"""

    #nb PCA
    """feature_matrix_reduced = functions.pca(feature_matrix, n_components)"""

    return feature_matrix, scaler
    #return feature_matrix_reduced, feature_matrix_Pxx, feature_list
