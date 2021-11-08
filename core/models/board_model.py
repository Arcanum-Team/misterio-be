from pony.orm import Required, PrimaryKey, Optional, Set
from core.models import db


class Enclosure(db.Entity):
    id = PrimaryKey(int)
    value = Required(str)
    doors = Set('Box')


class BoxType(db.Entity):
    id = PrimaryKey(int)
    value = Required(str)
    boxes = Set('Box')


class BoxAdjacent(db.Entity):
    id = PrimaryKey(int, auto=True)
    adj_box_id = Required(int)
    box = Required('Box')


class Box(db.Entity):
    id = PrimaryKey(int)
    row = Required(int)
    type = Required(BoxType)
    enclosure = Optional(Enclosure)
    adjacent_boxes = Set(BoxAdjacent)
    related_box = Optional(int)
    players = Set('Player')
