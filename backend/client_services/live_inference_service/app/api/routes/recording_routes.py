'''Routes for saving recordings'''
import requests
import pickle

from fastapi import Depends
from beanie import PydanticObjectId

from libs.authentication.user_token_auth import TokenData, token_authentication

from schemas.mongo_models.gesture import MongoGestureInformation
from app.api.main import app, redis
from app.api.tools.tools import data_to_numpy

@app.get("/save_recording/{session_id}/{gesture_id}", tags=['RecordingStreaming'])
async def get_save_recording(session_id : str, gesture_id: str, token_data: TokenData = Depends(token_authentication)):
    '''
    Take the last 0.5 seconds of recording data, download it and send it to the recording upload service
    '''
    gesture = await MongoGestureInformation.get(PydanticObjectId(gesture_id))
    if gesture is None:
        raise Exception

    data_length = await redis.llen(session_id)

    # TODO check that the current session if has the correct recording rate

    if data_length < 2*gesture.num_samples_per_recording:
        raise Exception

    data = await redis.lrange(str(session_id), -1*gesture.num_samples_per_recording, -1)
    data = data_to_numpy(data)

    # TODO use tmp
    pickle_file_path = '/data.pickle'
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)


    url = f'http://recording-upload-service:8080/recording/{gesture_id}'
    files = {'recording': open(pickle_file_path, 'rb')}
    response = requests.post(url, files=files, headers={'Authorization': f'Bearer {token_data.token}'})
    print(response.status_code)
    if response.status_code != 200 and response.status_code != 204:
        raise Exception
