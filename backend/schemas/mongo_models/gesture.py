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
    continuous : bool = False
    sampling_frequency_hz : int = 1000
    num_samples_per_recording : int = 500
    num_recordings_required : int = 10
    num_channels : int = 8
