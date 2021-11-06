from pony.orm import db_session

from core.models.players_model import Player
from core.schemas import BasicPlayerInfo


@db_session
def find_player_by_id(uuid):
    return Player[uuid]


def find_basic_player(uuid):
    player: Player = find_player_by_id(uuid)
    return BasicPlayerInfo(nickname=player.nickname)
