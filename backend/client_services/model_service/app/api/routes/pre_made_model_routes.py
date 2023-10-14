'''User Specific Information to pre made models'''
from schemas.mongo_models.pre_made_models import MongoPreMadeModel

from fastapi import Depends
from beanie import PydanticObjectId
from pydantic import BaseModel

from schemas.task_messages.model_training_task import TrainModelRequest
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.account_models import MongoAccount, TrainingState
from libs.authentication.user_token_auth import TokenData, token_authentication
from configs.commons import Tasks

from app.api.main import app, global_celery
from app.api.exceptions.not_found_exception import AccountNotFoundException


GestureID = str


class PreMadeModelInfo(BaseModel):
    '''Description of a model that can be deployed to a device'''

    class GestureInfo(BaseModel):
        '''Information about a gesture in a model'''
        name: str
        video_link: str
        photo_link: str
        gesture_id: GestureID
        num_recordings: int
        recording_complete_percentage: int
        continuous : bool

    name: str
    model_id : str
    training_state : TrainingState
    training_percentage : int
    gestures: list[GestureInfo]
    sample_period_s: float
    num_rest_recordings: int

class PreMadeModels(BaseModel):
    models : list[PreMadeModelInfo]


async def mongo_model_to_model_info(mongo_model: MongoPreMadeModel, account_model: MongoAccount) -> PreMadeModelInfo:
    '''Convert the mongo definition to a response to be sent to a user'''
    # print(account_model)
    return PreMadeModelInfo(
        name=mongo_model.name,
        model_id=str(mongo_model.id),
        training_state= account_model.models[str(mongo_model.id)].training_state if str(mongo_model.id) in account_model.models else TrainingState.NOT_STARTED,
        training_percentage = account_model.models[str(mongo_model.id)].training_percentage if str(mongo_model.id) in account_model.models else 0,
        sample_period_s=mongo_model.sample_period_s,
        gestures=[
            PreMadeModelInfo.GestureInfo(
                name=mongo_gesture.name,
                video_link=mongo_gesture.video_link,
                photo_link=mongo_gesture.photo_link,
                continuous=mongo_gesture.continuous,
                gesture_id=str(mongo_gesture.id),
                num_recordings=len(account_model.gestures[str(mongo_gesture.id)].user_recordings) if str(mongo_gesture.id) in account_model.gestures else 0,
                recording_complete_percentage = min(100,
                    100*int((len(account_model.gestures[str(mongo_gesture.id)].user_recordings)
                    if str(mongo_gesture.id) in account_model.gestures else 0)
                    / mongo_gesture.num_recordings_required))
            )
            for mongo_gesture in [await MongoGestureInformation.get(gesture_id) for gesture_id in mongo_model.gestures] if mongo_gesture is not None
        ],
        num_rest_recordings = 0
            if str(mongo_model.id) not in account_model.models else
            len(account_model.models[str(mongo_model.id)].rest_data_file_locations)
    )

@app.get('/pre_made_models', response_model = PreMadeModels, tags=['PreMadeModels'])
async def get_pre_made_models(token_data: TokenData = Depends(token_authentication)) -> PreMadeModels:
    '''Get a list of the pre made models'''
    mongo_account : MongoAccount = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    assert mongo_account is not None
    return PreMadeModels(
        models = [
            await mongo_model_to_model_info(
                mongo_model, mongo_account
            )
            async for mongo_model in MongoPreMadeModel.find_all()
        ]
    )


@app.post('/model/{model_id}', tags=['Models'])
async def post_model(model_id: str, token_data: TokenData = Depends(token_authentication)):
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)
    global_celery.send_task(Tasks.MODEL_TRAINING_TASK,
    kwargs={'request' : TrainModelRequest(
        account_id = str(mongo_account.id), training_model_id=model_id
    ).json()})
