from enum import Enum
from typing import NewType
from beanie import Document
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel

class TrainingState(Enum):

    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'

class MongoTrainingModel(Document):

    class MongoModelGestureInfo(BaseModel):

        gesture_name: str
        video_link: str
        photo_link: str
        gesture_id: str
        command: str

    creation_date: int
    name: str
    gestures: list[MongoModelGestureInfo]
    training_state: TrainingState
    account_id: PydanticObjectId
