'''General Numerical tools'''
import struct
import base64

import numpy as np


# OpenBCI Spec
# Bytes 2 to 26 are the 8 readings

PACKET_SIZE_BYTES = 33
NUM_BYTES_IN_INT = 3
NUM_CHANNELS = 8


def data_to_numpy(data: list[str]):
    '''Convert string encoded packets from redis to numpy array of readings from openBCI spec'''
    return [
        [int.from_bytes(byte_array[i:i+NUM_BYTES_IN_INT], byteorder='big', signed=True)
            for i in range(0, len(byte_array), NUM_BYTES_IN_INT)
        ] for byte_array in
        [base64.b64decode(reading_set.encode('utf8'))[2:NUM_CHANNELS*NUM_BYTES_IN_INT+2] for reading_set in data]
    ]
