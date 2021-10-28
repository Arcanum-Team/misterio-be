from pony.orm import Required, Set

from . import db


class Player(db.Entity):
    name = Required(str)
    nickname = Required(str)
    games = Set(lambda: db.Game)
    isHost = Required(bool)
