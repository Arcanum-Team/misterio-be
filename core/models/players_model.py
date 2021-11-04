import uuid

from pony.orm import Required, PrimaryKey, Optional, Set, IntArray

from . import db
from .games_model import Game


class Player(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    nickname = Required(str, max_len=20)
    game = Required(Game)
    host = Required(bool, default=False)
    order = Optional(int)
    cards = Required(IntArray, default=[])
    witch= Optional(bool, default=False)