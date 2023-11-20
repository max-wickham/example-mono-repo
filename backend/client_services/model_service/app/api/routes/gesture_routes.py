'''User Specific Information to pre made models'''
import zipfile
import io

from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse
from beanie import PydanticObjectId
from pydantic import BaseModel

from schemas.task_messages.model_training_task import TrainModelRequest
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.account_models import MongoAccount, TrainingState
from schemas.mongo_models.pre_made_models import MongoPreMadeModel
from libs.authentication.user_token_auth import TokenData, token_authentication


from app.api.configs import Tasks
from app.api.main import app, celery, s3
from app.api.exceptions.not_found_exception import AccountNotFoundException
from app.api.routes.tasks import DeleteRecordingsTask, delete_recordings_task
from app.api.configs import Config

GestureID = str

class Gestures(BaseModel):
    '''Available gestures and the current state of each gesture'''

    class Gesture(BaseModel):
        '''Information regarding a single gesture'''
        name : str
        num_recordings: int
        recording_completion_percentage: int
        gesture_id : GestureID
        sample_frequency_hz : int
        continuous : bool
        num_channels : int
        num_samples : int

    # dict of gesture id to gesture info
    gestures : dict[GestureID,Gesture]

@app.get('/gestures', response_model=Gestures, tags=["Gestures"])
async def get_gestures(token_data: TokenData = Depends(token_authentication)) -> Gestures:
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)

    mongo_gestures = MongoGestureInformation.find()

    response_gestures = Gestures(
        gestures = {str(gesture.id) : Gestures.Gesture(
            name=gesture.name,
            continuous=gesture.continuous,
            num_recordings = 0
                if str(gesture.id) not in mongo_account.gestures.keys() else
                len(mongo_account.gestures[str(gesture.id)].user_recordings),
            recording_completion_percentage = min(100,int((0
                if str(gesture.id) not in mongo_account.gestures.keys() else
                len(mongo_account.gestures[str(gesture.id)].user_recordings))
                / gesture.num_recordings_required * 100)),
            gesture_id=str(gesture.id),
            sample_frequency_hz = gesture.sampling_frequency_hz,
            num_channels=gesture.num_channels,
            num_samples=gesture.num_samples_per_recording,
        ) async for gesture in mongo_gestures }
    )

    return response_gestures

class GestureRequest(BaseModel):
    '''Information to create a new pre made model'''
    name : str = ""
    comments : str = ""
    video_link : str = ""
    photo_link: str = ""
    continuous : bool = False
    sampling_frequency_hz : int = 1000
    num_samples_per_recording : int = 500
    num_recordings_required : int = 10
    num_channels : int = 8

@app.post('/gesture', tags=['Gestures'])
async def post_gesture(
    gesture_request: GestureRequest, token_data: TokenData = Depends(token_authentication)):
    '''Create a new gesture'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    mongo_gesture = MongoGestureInformation(**gesture_request.dict())
    await mongo_gesture.save()

@app.delete('/gesture/{gesture_id}', tags=['Gestures'])
async def del_gesture(gesture_id: str, token_data: TokenData = Depends(token_authentication)):
    '''Delete an existing gesture globally'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    mongo_gesture = await MongoGestureInformation.get(PydanticObjectId(gesture_id))
    assert mongo_gesture is not None
    await mongo_gesture.delete()
    delete_recordings_task.apply_async(args=[ DeleteRecordingsTask(
        gesture_id = gesture_id
    ).json()], queue = Config.application_name)
    # celery.send_task(Tasks.DELETE_RECORDINGS_TASK,
    # kwargs={'request' : DeleteRecordingsTask(
    #     gesture_id = gesture_id
    # ).json()})
