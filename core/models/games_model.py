from typing import Optional
import uuid
from fastapi.datastructures import Default

from pony.orm import Required, Set, PrimaryKey, IntArray
from core.schemas.player_schema import Position
from . import db


class Game(db.Entity):
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    name = Required(str, max_len=20, unique=True)
    started = Required(bool, default=False)
    turn = Required(int, default= 1)
    Envelop = Required(IntArray, default=[])
    players = Set('Player')