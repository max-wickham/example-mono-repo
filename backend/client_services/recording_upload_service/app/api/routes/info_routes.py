'''Upload Routes'''
from fastapi import Depends
from beanie import PydanticObjectId
from pydantic import BaseModel
from schemas.mongo_models.gesture import MongoGestureInformation

from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, s3
from app.api.exceptions.not_found_exception import AccountNotFoundException


class Gestures(BaseModel):
    '''Available gestures and the current state of each gesture'''

    class Gesture(BaseModel):
        '''Information regarding a single gesture'''
        name : str
        num_recordings: str
        recording_completion_percentage: str
        gesture_id : str

    # dict of gesture id to gesture info
    gestures : dict[str,Gesture]

MAX_RECORDINGS = 10

@app.get('/gestures', response_model=Gestures)
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
            name=gesture.gesture_name,
            num_recordings = 0
                if gesture.id not in mongo_account.gestures else
                len(mongo_account.gestures[gesture.id].user_recordings),
            recording_completion_percentage = int((0
                if gesture.id not in mongo_account.gestures else
                len(mongo_account.gestures[gesture.id].user_recordings))
                / MAX_RECORDINGS * 100),
            gesture_id=gesture.id
        )
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
