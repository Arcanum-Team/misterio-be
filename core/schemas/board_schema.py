from typing import Optional, List
from pydantic.main import BaseModel


class EnclosureOutput(BaseModel):
    id: int
    name: str
    doors: Optional[List['BoxOutput']]


class BoxOutput(BaseModel):
    id: int
    position: Optional[int]
    attribute: str
    enclosure: Optional[EnclosureOutput]


class RowOutput(BaseModel):
    id: int
    boxes: List[BoxOutput]


class BoardOutput(BaseModel):
    rows: List[RowOutput]
    enclosures: List[EnclosureOutput]
