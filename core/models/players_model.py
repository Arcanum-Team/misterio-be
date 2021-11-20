import uuid

from pony.orm import Required, PrimaryKey, Optional, Set

from core.models import db, Game


class Player(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    nickname = Required(str, max_len=20)
    game = Required(Game)
    host = Required(bool, default=False)
    loser = Required(bool, default=False)
    order = Optional(int)
    cards = Set('Card')
    color = Optional(str)
    current_position = Optional('Box')
    enclosure = Optional('Enclosure')
    