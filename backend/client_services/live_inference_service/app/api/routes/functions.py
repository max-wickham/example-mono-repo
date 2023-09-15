import numpy as np
from scipy import signal
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
# import matplotlib.pyplot as plt

# from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn import svm
from scipy.signal import butter, lfilter

# from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, NoiseTypes



#NB functions for PRE-PROCESSING
def segmentation(x, window, overlap, channels_position):
    if channels_position == 'last':
        x = np.transpose(x)
    #input signal x in the form channels x time
    window = int(window)
    overlap = int(overlap)
    shift = window - overlap
    signal_lenght = x.shape[1]
    nr_channels = x.shape[0]

    # compute the number of windows which will fit:
    max_windows = int((signal_lenght - overlap)/shift)
    segmented_signal = np.zeros([max_windows, nr_channels, window]) # empty matrix

    for i in range(max_windows):
        segmented_signal[i, :, :] = x[:, (i*shift):(i*shift+window)]
    return segmented_signal

def detrend(data):
    break_points = list(range(0, data.shape[-1] + 1, int(0.01 * data.shape[-1]))) # use n_points = 1% of the size
    detrended_signal = signal.detrend(data, bp=break_points)
    return detrended_signal

def notch(input_signal, f0, fs):
    # f0 is Notch frequency (Hz)
    Q = 20  # Notch quality factor
    b, a = signal.iirnotch(f0, Q, fs)
    # Apply the notch filter to the signal
    signal_output = signal.lfilter(b, a, input_signal)

    return signal_output

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data, axis=-1)
    return y

def real_time_processing(input_signal, fs, n_channels, f_notch, f_low, f_high):
    #processed_data = []

    processed_data = detrend(input_signal)
    processed_data = notch(processed_data, 50, fs)
    processed_data = notch(processed_data, f_notch, fs)
    processed_data = butter_bandpass_filter(processed_data, f_low, f_high, fs, order=4)
    processed_data = detrend(processed_data)

    """for i in range(n_channels):
        input = input_signal[i, :]
        temp = DataFilter.perform_bandpass(input,fs,20.0, 500.0, 3, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0) #bandpass
        temp = processed_data = DataFilter.perform_bandstop(temp, fs, 48.0, 52.0, 3, FilterTypes.BUTTERWORTH_ZERO_PHASE, 0) # notch
        processed_data.append(temp)"""
    return processed_data

def shuffle_arrays_in_sync(array1, array2):
    # Generate a random permutation of indices
    permutation = np.random.permutation(array1.shape[0])

    # Shuffle both arrays using the same permutation
    shuffled_array1 = array1[permutation]
    shuffled_array2 = array2[permutation]

    return shuffled_array1, shuffled_array2

def pca(data, param):
    # Instantiate PCA with desired number of components
    pca = PCA(n_components=param)

    # Perform dimensionality reduction
    reduced_data = pca.fit_transform(data)

    return reduced_data

def feature_importance(feature_matrix, labels, plot):
    rf = RandomForestClassifier()
    rf.fit(feature_matrix, labels)

    feature_importance = rf.feature_importances_

    # if plot==True:
    #     axis = np.arange(len(feature_importance))
    #     #plt.hist(feature_importance[:], bins='auto', edgecolor='black')
    #     plt.bar(axis, feature_importance)
    #     plt.ylabel('Importance')
    #     plt.xlabel('Feature')
    #     plt.title('Feature-importance plot')
    #     plt.show()

    return feature_importance

def SVM_testing(feature_matrix, labels):
    # can't reshuffle everytime, otherwise comparison does not make sense
    # X_train, X_test, y_train, y_test = train_test_split(feature_matrix, labels, test_size=0.2, random_state=42)

    test_size = 0.2
    train_size = int((1-test_size)*len(feature_matrix))

    X_train = feature_matrix[0:train_size, :]
    X_test = feature_matrix[train_size:, :]
    y_train = labels[0:train_size]
    y_test = labels[train_size:]

    classifier = svm.SVC()

    # Train the classifier
    classifier.fit(X_train, y_train)

    # Make predictions on the test set
    predictions = classifier.predict(X_test)

    # Calculate the accuracy of the classifier
    accuracy = accuracy_score(y_test, predictions)
    # Generate the classification report
    report = classification_report(y_test, predictions)

    print("Accuracy:", accuracy)
    print("Classification Report:")
    print(report)

    return accuracy


def SVM_testing(feature_matrix, labels):
    # can't reshuffle everytime, otherwise comparison does not make sense
    # X_train, X_test, y_train, y_test = train_test_split(feature_matrix, labels, test_size=0.2, random_state=42)

    test_size = 0.2
    train_size = int((1-test_size)*len(feature_matrix))

    X_train = feature_matrix[0:train_size, :]
    X_test = feature_matrix[train_size:, :]
    y_train = labels[0:train_size]
    y_test = labels[train_size:]

    # -----------
    # ML starts from here

    classifier = svm.SVC()

    # Train the classifier
    classifier.fit(X_train, y_train)

    # Make predictions on the test set
    predictions = classifier.predict(X_test)

    # Calculate the accuracy of the classifier
    accuracy = accuracy_score(y_test, predictions)
    # Generate the classification report
    report = classification_report(y_test, predictions)

    print("Accuracy:", accuracy)
    print("Classification Report:")
    print(report)

    return accuracy
