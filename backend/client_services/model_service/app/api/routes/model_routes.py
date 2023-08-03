'''Upload Routes'''
import time
from enum import Enum

from fastapi import Depends, Body
from beanie import PydanticObjectId
from pydantic import BaseModel

from schemas.mongo_models.training_models import MongoTrainingModel
from schemas.mongo_models.gesture import MongoGestureInformation
from schemas.mongo_models.account_models import MongoAccount
from libs.authentication.user_token_auth import TokenData, token_authentication

from app.api.main import app, s3
from app.api.exceptions.not_found_exception import AccountNotFoundException

GestureID = str


class ModelInfo(BaseModel):
    '''Description of a model that can be deployed to a device'''

    class TrainingState(Enum):
        '''Describes whether or not the model has completed training and is ready to be deployed'''

        NOT_STARTED = 'not_started'
        IN_PROGRESS = 'in_progress'
        COMPLETE = 'complete'

    class GestureInfo(BaseModel):
        '''Information about a gesture in a model'''
        name: str
        command: str
        video_link: str
        photo_link: str
        gesture_id: GestureID

    name: str
    creation_date: int
    training_state: TrainingState
    gestures: list[GestureInfo]


class Models(BaseModel):
    '''Response describing list of models to be sent to user'''
    models: list[ModelInfo]


def mongo_model_to_model_info(mongo_model: MongoTrainingModel) -> ModelInfo:
    '''Convert the mongo definition to a response to be sent to a user'''
    return ModelInfo(
        name=mongo_model.name,
        creation_date=mongo_model.creation_date,
        training_state=mongo_model.training_state,
        gestures=[
            ModelInfo.GestureInfo(
                name=mongo_gesture.gesture_name,
                command=mongo_gesture.command,
                video_link=mongo_gesture.photo_link,
                photo_link=mongo_gesture.photo_link,
                gesture_id=mongo_gesture.gesture_id
            )
            for mongo_gesture in mongo_model.gestures
        ]
    )


@app.get('/models', response_model=Models, tags='Models')
async def get_models(token_data: TokenData = Depends(token_authentication)) -> Models:
    '''Get a list of models defined by the user'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)

    response = Models(
        models=[
            mongo_model_to_model_info(
                await MongoTrainingModel.get(mongo_model_id)
            )
            for mongo_model_id in mongo_account.models
        ]
    )
    return response


class GestureDefinition(BaseModel):
    '''Information about the gesture in a model'''
    gesture_id: GestureID
    command: str


class ModelDefinition(BaseModel):
    '''Request to create a new model'''
    gestures: list[GestureDefinition]
    model_name: str


@app.post('/model')
async def post_model(model_definition: ModelDefinition = Body(...),
                     token_data: TokenData = Depends(token_authentication)) -> ModelInfo:
    '''Create a new model'''
    mongo_account = await MongoAccount.get(PydanticObjectId(token_data.account_id))
    if mongo_account is None:
        raise AccountNotFoundException(token_data.account_id)

    mongo_gestures = [
        await MongoGestureInformation.get(PydanticObjectId(definition.gesture_id)) for
        definition in model_definition.gestures
    ]

    mongo_training_model = MongoTrainingModel(
        creation_date=int(time.time()),
        name=model_definition.model_name,
        gestures=[
            MongoTrainingModel.MongoModelGestureInfo(
                gesture_name=gesture.name,
                video_link=gesture.video_link,
                photo_link=gesture.photo_link,
                gesture_id=gesture.id,
                command=model_definition.gestures[i].command
            )
            for i, gesture in enumerate(mongo_gestures)
        ]
    )
    mongo_training_model.account_id = PydanticObjectId(token_data.account_id)
    await mongo_training_model.save()
    mongo_account.models.append(mongo_training_model.id)
    await mongo_account.save()
    return mongo_model_to_model_info(mongo_training_model)