from pony.orm import db_session

from core.models import Game
from core.models.players_model import Player
from core.schemas import BasicPlayerInfo, PlayerOutput
from core.schemas.card_schema import CardBasicInfo
from core.schemas.player_schema import GameInDB, BoxOutput


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
def find_player_by_id_and_game_id(player_id, game_id):
    player: Player = find_player_by_id(player_id)
    return PlayerOutput(id=player.id,
                        nickname=player.nickname,
                        host=player.host,
                        game=GameInDB.from_orm(player.game),
                        current_position=BoxOutput(
                            id=player.current_position.id,
                            attribute=player.current_position.type.value)
                        )
