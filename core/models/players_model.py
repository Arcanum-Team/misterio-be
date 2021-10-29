import uuid

from pony.orm import Required, PrimaryKey

from . import db
from .games_model import Game


class Player(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    nickname = Required(str, max_len=20)
    game = Required(Game)
    is_host = Required(bool, default=False)
