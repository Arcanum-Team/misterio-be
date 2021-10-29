import uuid

from pony.orm import Required, Set, PrimaryKey

from . import db


class Game(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    name = Required(str, max_len=20, unique=True)
    started = Required(bool, default=False)
    players = Set('Player')
