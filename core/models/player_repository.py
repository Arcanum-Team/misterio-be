from pony.orm import db_session

from core.models.players_model import Player


@db_session
def find_player_by_id(uuid):
    return Player[uuid]
