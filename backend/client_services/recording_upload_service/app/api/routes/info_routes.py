'''Upload Routes'''
from fastapi import Depends
from beanie import PydanticObjectId
from pydantic import BaseModel
from schemas.mongo_models.gesture import MongoGestureInformation

from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, s3
from app.api.exceptions.not_found_exception import AccountNotFoundException


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

    # dict of gesture id to gesture info
    gestures : dict[GestureID,Gesture]

@app.get('/gestures', response_model=Gestures, tags=["GestureInfo"])
async def get_gestures(token_data: TokenData = Depends(token_authentication)) -> Gestures:
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)

    mongo_gestures = MongoGestureInformation.find()

    response_gestures = Gestures(
        gestures = {}
    )
    async for gesture in mongo_gestures:
        response_gestures.gestures[str(gesture.id)] = Gestures.Gesture(
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
            sample_frequency_hz = gesture.sampling_frequency_hz
        )
    return response_gestures

@app.delete('/gesuture_recordings/{gesture_id}', tags=["GestureInfo"])
async def delete_gesture_recordings(gesture_id: str, token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    # TODO delete gestures from S3 !!!!!
    if gesture_id in mongo_account.gestures:
        mongo_account.gestures[gesture_id].user_recordings = []
        mongo_account.gestures[gesture_id].processed_user_recordings = []
        await mongo_account.save()

@app.delete('/rest_recordings/{model_id}', tags=["GestureInfo"])
async def delete_gesture_recordings(gesture_id: str, token_data: TokenData = Depends(token_authentication)):
    '''Upload a binary recording file of the sensor data'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    # TODO delete gestures from S3 !!!!!
    if model_id in mongo_account.models:
        mongo_account.models[model_id].rest_data_file_locations = []
        await mongo_account.save()
