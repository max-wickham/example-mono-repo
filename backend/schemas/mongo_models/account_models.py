'''Models representing company accounts and company information'''

from enum import Enum
from typing import NewType
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

from schemas.mongo_models.gesture import MongoAccountGestureRecordings

LabelName = NewType('LabelName',str)

GestureID = str
MongoTrainingModelID = str

class TrainingState(Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'

class UserFineTunedModel(BaseModel):
    '''User fine tuned model'''
    pre_made_model_id: PydanticObjectId
    training_state: TrainingState = TrainingState.NOT_STARTED
    model_location: str = ''


class MongoAccount(Document):
    '''Basic Account'''
    name: str
    email: str
    password_hash : str
    gestures : dict[GestureID,MongoAccountGestureRecordings] = {}
    models: dict[str, UserFineTunedModel] = {}
