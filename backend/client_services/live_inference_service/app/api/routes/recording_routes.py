'''Routes for saving recordings'''
import requests
import pickle

from fastapi import Depends
from beanie import PydanticObjectId
from schemas.mongo_models.pre_made_models import MongoPreMadeModel

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
    print(data_length)
    print(session_id)
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


@app.get("/save_rest_recording/{session_id}/{model_id}", tags=['RecordingStreaming'])
async def get_save_rest_recording(session_id : str, model_id: str, token_data: TokenData = Depends(token_authentication)):
    '''
    Take the last 0.5 seconds of recording data, download it and send it to the recording upload service
    '''
    model = await MongoPreMadeModel.get(PydanticObjectId(model_id))
    if model is None:
        raise Exception

    data_length = await redis.llen(session_id)
    # TODO check that the current session if has the correct recording rate

    if data_length < 2*model.sample_number:
        raise Exception

    data = await redis.lrange(str(session_id), -1*model.sample_number, -1)
    data = data_to_numpy(data)

    # TODO use tmp
    pickle_file_path = '/data.pickle'
    with open(pickle_file_path, 'wb') as pickle_file:
        pickle.dump(data, pickle_file)


    url = f'http://recording-upload-service:8080/rest_recording/{model_id}'
    files = {'recording': open(pickle_file_path, 'rb')}
    response = requests.post(url, files=files, headers={'Authorization': f'Bearer {token_data.token}'})
    print(response.status_code)
    if response.status_code != 200 and response.status_code != 204:
        raise Exception


@app.get('/stream_active/{stream_id}', tags=["StreamInfo"], response_model=bool)
async def get_stream_active(stream_id: str) -> bool:
    try:
        return (await redis.object('idletime', stream_id)) < 1
    except:
        return False

@app.get('/stream_channel_count/{stream_id}', tags=["StreamInfo"], response_model=int)
async def get_stream_channel_count(stream_id: str) -> int:
    try:

        result : int | None = await redis.get(f'{stream_id}_CHANNEL_COUNT')
        if result is None:
            return 0
        else:
            return result
    except:
        return 0

@app.get('/stream_frequency/{stream_id}', tags=["StreamInfo"], response_model=int)
async def get_stream_frequency(stream_id: str) -> int:
    try:

        result : int | None = await redis.get(f'{stream_id}_FREQUENCY_HZ')
        if result is None:
            return 0
        else:
            return result
    except:
        return 0
