from enum import Enum
from typing import NewType
from beanie import Document
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel

FileName = str

class MongoPreMadeModel(Document):

    name: str
    gestures : list[PydanticObjectId]
    model_weights : FileName
