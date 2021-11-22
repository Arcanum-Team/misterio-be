from typing import Set

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
def exit_enclosure(player_id, box_id):
    player: Player = find_player_by_id(player_id)
    assert player.enclosure is not None
    assert player.current_position is None

    box: Box = next(filter(lambda b: b.id == box_id, player.enclosure.doors), None)

    assert box is not None

    player.enclosure = None
    player.current_position = box
    return GamePlayer(
        game=GameOutput.from_orm(player.game),
        player=player_to_player_output(player)
    )


@db_session
def player_to_player_output(player):
    output: PlayerOutput = PlayerOutput(id=player.id, nickname=player.nickname, host=player.host, order=player.order,
                                        witch=player.witch, loser=player.loser)
    if player.current_position:
        output.current_position = BoxOutput(id=player.current_position.id, attribute=player.current_position.type.value)
    if player.enclosure:
        output.enclosure = EnclosureOutput(
            id=player.enclosure.id,
            name=player.enclosure.value,
            doors=[BoxOutput(id=door.id, attribute=door.type.value) for door in player.enclosure.doors]
        )
    return output


@db_session
def find_available_players_without_me(player_in_shift: Player):
    return set(filter(lambda p: p.id != player_in_shift.id and not p.loser, player_in_shift.game.players))


def get_next_turn(current_turn, max_turn_value):
    t = 1
    if current_turn < max_turn_value:
        t = current_turn + 1
    return t


@db_session
def find_next_available_player(player_in_shift: Player):
    available_players: Set[Player] = find_available_players_without_me(player_in_shift)
    max_turn_value: int = len(player_in_shift.game.players)
    next_player = None
    current_turn: int = player_in_shift.order
    while not next_player:
        next_turn: int = get_next_turn(current_turn, max_turn_value)
        next_player = next(filter(lambda p: p.order == next_turn, available_players), None)
    return next_player


@db_session
def find_player_enclosure(player_id):
    player: Player = find_player_by_id(player_id)
    assert player.enclosure != None
    return player.enclosure.id


@db_session
def is_player_card(player_id, card_id):
    player: Player = find_player_by_id(player_id)
    cards = list(map(lambda x: x.id, player.cards))
    assert card_id in cards
