from typing import Optional, List
from pydantic.main import BaseModel


class BoxOutput(BaseModel):
    position: int
    row: int
    attribute: str
    enclosure_id: Optional[int]
    arrow: str
    row_id: Optional[int]



class EnclosureOutput(BaseModel):
    id: int
    name: str
    doors: List[BoxOutput]


class RowOutput(BaseModel):
    position: int
    boxes:List[BoxOutput]


class BoardOutput(BaseModel):
    rows: List[RowOutput]
    enclosures:List[EnclosureOutput]
