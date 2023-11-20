'''General Numerical tools'''
import struct
import base64

import numpy as np

from configs.commons import StreamingConfigs

NUM_BYTES_IN_INT = StreamingConfigs.BYTES_PER_INT

def data_to_numpy(data: list[str]):
    '''Convert string encoded packets from redis to numpy array of readings from openBCI spec'''
    # packet_size_bytes = NUM_BYTES_IN_INT * num_channels
    return np.array([
        [int.from_bytes(byte_array[i:i+NUM_BYTES_IN_INT], byteorder='big', signed=True)
            for i in range(0, len(byte_array), NUM_BYTES_IN_INT)
        ] for byte_array in
        [base64.b64decode(reading_set.encode('utf8')) for reading_set in data]
    ])
