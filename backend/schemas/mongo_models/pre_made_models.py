from enum import Enum
from datetime import datetime
from typing import NewType
from beanie import Document
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel, Field

FileName = str

class MongoPreMadeModel(Document):

    name: str
    gestures : list[PydanticObjectId]
    model_weights : FileName
    creation_date : int = Field(default_factory=datetime.now().timestamp)
