from pony.orm import Required, Set

from . import db


class Game(db.Entity):
    name = Required(str)
    started = Required(bool, default=False)
    players = Set(lambda: db.Player)
