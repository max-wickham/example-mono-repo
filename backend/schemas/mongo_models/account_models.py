'''Models representing company accounts and company information'''

from enum import Enum
from datetime import datetime
from typing import NewType

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

LabelName = NewType('LabelName',str)

GestureID = str
MongoTrainingModelID = str

class TrainingState(Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'

class TrainingInformation(BaseModel):
    '''Information about a training of a model'''
    creation_date : int = Field(default_factory=datetime.now().timestamp)

class UserFineTunedModel(BaseModel):
    '''User fine tuned model'''
    pre_made_model_id: PydanticObjectId
    name : str
    creation_date : int = Field(default_factory=datetime.now().timestamp)
    training_logs : list[TrainingInformation] = []
    training_state: TrainingState = TrainingState.NOT_STARTED
    model_location: str = ''

class MongoAccountGestureRecordings(BaseModel):
    '''Information about a gesture for a user'''
    gesture_id: PydanticObjectId
    user_recordings : list[str] = []
    processed_user_recordings : list[str] = []

class MongoAccount(Document):
    '''Basic Account'''
    name: str
    email: str
    password_hash : str
    gestures : dict[GestureID,MongoAccountGestureRecordings] = {}
    models: dict[str, UserFineTunedModel] = {}
