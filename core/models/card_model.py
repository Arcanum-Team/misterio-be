import uuid
from fastapi.datastructures import Default
from pony.orm import Required, Set, PrimaryKey
from . import db
from .games_model import Game

class Card(db.Entity):
    id = PrimaryKey(int, default=0)
    name = Required(str)
    type = Required(str)
