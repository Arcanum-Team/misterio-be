from enum import Enum
from typing import Optional

from pydantic import BaseModel


class BoxType(str, Enum):
    NONE = "NONE"
    TRAP = "TRAP"
    ENTRY = "ENTRY"
    ENCLOSURE_LEFT = "ENCLOSURE_LEFT"
    ENCLOSURE_RIGHT = "ENCLOSURE_RIGHT"
    ENCLOSURE_UP = "ENCLOSURE_UP"
    ENCLOSURE_DOWN = "ENCLOSURE_DOWN"


class Box(BaseModel):
    row_id: int
    id: int
    enclosure_id: Optional[int]
    cross_row_id: Optional[int]
    type: BoxType

