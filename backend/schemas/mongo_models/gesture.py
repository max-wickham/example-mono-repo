from typing import NewType
from beanie import Document
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel

LabelName = NewType('LabelName',str)


class MongoGestureInformation(Document):
    '''Information about a gesture'''
    gesture_name : str
    gesture_comments : str
    gesture_video_link : str

class MongoAccountGestureRecordings(Document):
    '''Information about a gesture for a user'''
    gesture_name : str
    user_recordings : list[str]
