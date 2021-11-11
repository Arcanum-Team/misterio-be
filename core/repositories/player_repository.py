from pony.orm import db_session

from core.models import Box
from core.models.players_model import Player
from core.schemas import BasicPlayerInfo, PlayerOutput, BoxOutput
from core.schemas.card_schema import CardBasicInfo
from core.schemas.player_schema import GameInDB


@db_session
def find_player_by_id(uuid):
    return Player[uuid]


@db_session
def find_basic_player(uuid):
    player: Player = find_player_by_id(uuid)
    return BasicPlayerInfo(nickname=player.nickname)


@db_session
def get_cards_by_player_id(player_id):
    player: Player = find_player_by_id(player_id)
    return [CardBasicInfo(id=card.id, name=card.name, type=card.type) for card in player.cards]


@db_session
def update_current_position(player_id, position):
    player: Player = find_player_by_id(player_id)
    player.current_position = Box[position]
    return PlayerOutput(id=player.id,
                        nickname=player.nickname,
                        host=player.host,
                        game=GameInDB.from_orm(player.game),
                        current_position=BoxOutput(
                            id=player.current_position.id,
                            attribute=player.current_position.type.value)
                        )

@db_session
def set_loser(player_id):
    player: Player = find_player_by_id(player_id)
    player.loser = True