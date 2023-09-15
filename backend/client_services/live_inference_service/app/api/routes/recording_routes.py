'''Routes for saving recordings'''
import requests
import struct
import base64
import pickle

from fastapi import File, UploadFile, Depends
from beanie import PydanticObjectId
import numpy as np

from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, redis, s3
from app.api.tools.tools import data_to_numpy

NUM_READINGS = 500
NUM_CHANNELS = 8

@app.get("/save_recording/{session_id}/{gesture_id}", tags=['RecordingStreaming'])
async def get_save_recording(session_id : str, gesture_id: str, token_data: TokenData = Depends(token_authentication)):
    '''
    Take the last 0.5 seconds of recording data, download it and send it to the recording upload service
    '''

    data_length = await redis.llen(session_id)
    if data_length < 2*NUM_READINGS:
        raise Exception

    data = await redis.lrange(str(session_id), -1*NUM_READINGS, -1)
    # data = np.array([struct.unpack(f'{NUM_CHANNELS}f', base64.b64decode(reading_set.encode('utf8'))) for reading_set in data])
    data = data_to_numpy(data)
    pickle_file_path = '/data.pickle'
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)


    url = f'http://recording-upload-service:8080/recording/{gesture_id}'
    files = {'recording': open(pickle_file_path, 'rb')}
    response = requests.post(url, files=files, headers={'Authorization': f'Bearer {token_data.token}'})
    print(response.status_code)
    if response.status_code != 200 and response.status_code != 204:
        raise Exception
