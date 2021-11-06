from typing import Optional
from pony.orm import Required, Set, PrimaryKey, Optional
from . import db

class Box(db.Entity):
    id = PrimaryKey(int, default=1)
    row = Required(int)
    attribute = Required(str, default="NONE")
    enclosure_id = Required(int, default=0) 
    arrow = Required(str, default="NONE")
    row_id = Optional(int)

