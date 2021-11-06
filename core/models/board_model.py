from pony.orm import Required, PrimaryKey, Optional, Set

from core.models import db


class Box(db.Entity):
    id = PrimaryKey(int, default=1)
    attribute = Required(str, default="NONE")
    enclosure_id = Required(int, default=0)
    arrow = Required(str, default="NONE")
    row_id = Optional(int)
    players = Set('Player')
