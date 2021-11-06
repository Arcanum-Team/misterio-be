from pony.orm import PrimaryKey, Required, Optional, Set

from core.models import db


class Enclosure(db.Entity):
    id = PrimaryKey(int)
    name = Required(str)
    boxes = Set('Box')


class BoxType(db.Entity):
    id = PrimaryKey(int)
    value = Required(str)
    boxes = Set('Box')


class Box(db.Entity):
    id = PrimaryKey(int)
    row_id = Required(str)
    type = Required(BoxType)
    enclosure = Optional(Enclosure)
    cross_row_id = Optional(int)
    players = Set('Player')
