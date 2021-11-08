from uuid import UUID
from pony.orm import Required, PrimaryKey, Set
from core.models import db


class Card(db.Entity):
    id = PrimaryKey(int)
    name = Required(str)
    type = Required(str)
    players = Set('Player')
