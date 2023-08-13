'''Models representing company accounts and company information'''

from typing import NewType
from beanie import Document

from schemas.mongo_models.gesture import MongoAccountGestureRecordings

LabelName = NewType('LabelName',str)

GestureID = str
MongoTrainingModelID = str

class MongoAccount(Document):
    '''Basic Account'''
    name: str
    email: str
    password_hash : str
    gestures : dict[GestureID,MongoAccountGestureRecordings] = {}
    models: list[MongoTrainingModelID] = []
