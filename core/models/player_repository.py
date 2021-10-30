from pony.orm import db_session, select

from core.models.players_model import Player


@db_session
def get_player_by_id():
    return select(p for p in Player if p.id == id)[:]
