'''Models representing company accounts and company information'''

from typing import NewType
from beanie import Document
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel

LabelName = NewType('LabelName',str)

class MongoAccount(Document):
    '''Basic Account'''
    name: str
    email: str
    password_hash : str

    recording_files : list[str] = []
