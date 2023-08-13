from typing import NewType
from beanie import Document
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel

LabelName = NewType('LabelName',str)


class MongoGestureInformation(Document):
    '''Information about a gesture'''
    name : str
    comments : str
    video_link : str
    photo_link: str

class MongoAccountGestureRecordings(BaseModel):
    '''Information about a gesture for a user'''
    gesture_id: PydanticObjectId
    user_recordings : list[str] = []
    processed_user_recordings : list[str] = []
