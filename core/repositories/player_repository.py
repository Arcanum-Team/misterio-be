from pony.orm import db_session

from core.models import Box
from core.models.players_model import Player
from core.schemas import BasicPlayerInfo, PlayerOutput, BoxOutput, GamePlayer, GameOutput
from core.schemas.card_schema import CardBasicInfo
from core.schemas.player_schema import EnclosureOutput


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
    return player_to_player_output(player)


@db_session
def set_loser(player_id):
    player: Player = find_player_by_id(player_id)
    player.loser = True


@db_session
def enter_enclosure(player_id):
    player: Player = find_player_by_id(player_id)
    assert player.enclosure is None
    assert player.current_position.type.value in ["ENCLOSURE_DOWN", "ENCLOSURE_UP"]
    player.enclosure = player.current_position.enclosure
    player.current_position = None
    return GamePlayer(
        game=GameOutput.from_orm(player.game),
        player=player_to_player_output(player)
    )


@db_session
def player_to_player_output(player):
    output: PlayerOutput = PlayerOutput(id=player.id, nickname=player.nickname, host=player.host, order=player.order)
    if player.current_position:
        output.current_position = BoxOutput(id=player.current_position.id, attribute=player.current_position.type.value)
    if player.enclosure:
        output.enclosure = EnclosureOutput(
            id=player.enclosure.id,
            name=player.enclosure.value,
            doors=[BoxOutput(id=door.id, attribute=door.type.value) for door in player.enclosure.doors]
        )
    return output
