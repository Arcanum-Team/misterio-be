from typing import List
import uuid
from pydantic import validator, Field
from pydantic.main import BaseModel
from uuid import UUID

class CardBasicInfo(BaseModel):
    id: UUID
    name: str
    type: str

    class Config:
        orm_mode = True


