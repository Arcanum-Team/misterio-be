from pony.orm import Required, Set, PrimaryKey, Optional
from . import db


class Box(db.Entity):
    id = PrimaryKey(int, default=1)
    row = Required(int)
    attribute = Required(str, default="NONE")
    enclosure_id = Optional('Enclosure')
    arrow = Required(str, default="NONE")
    row_id = Optional(int)
    players = Set('Player')


class Enclosure(db.Entity):
    id = PrimaryKey(int, default=0)
    name = Required(str)
    doors = Set(Box)
