from typing import Optional, List
from uuid import UUID

from pydantic import validator, Field
from pydantic.main import BaseModel

class BoxOutput(BaseModel):
    position: int
    row: int
    attribute: str
    enclosure_id: int
    arrow: str
    row_id: Optional[int]


class RowOutput(BaseModel):
    position: int
    boxes:List[BoxOutput]
