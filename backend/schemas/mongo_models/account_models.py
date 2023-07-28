'''Models representing company accounts and company information'''

from typing import NewType
from beanie import Document
from beanie.odm.fields import PydanticObjectId

from schemas.mongo_models.gesture import MongoAccountGestureRecordings

LabelName = NewType('LabelName',str)



class MongoAccount(Document):
    '''Basic Account'''
    name: str
    email: str
    password_hash : str
    gestures : dict[PydanticObjectId,MongoAccountGestureRecordings] = {}
