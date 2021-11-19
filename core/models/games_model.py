import uuid
from pony.orm import Required, Set, PrimaryKey, IntArray, Optional
from core.models import db


class Game(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    name = Required(str, max_len=20, unique=True, index=True)
    started = Required(bool, default=False)
    turn = Optional(int)
    envelop = Required(IntArray, default=[])
    players = Set('Player')
    in_enclosure=Optional(bool, default=False)
