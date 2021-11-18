import json
from uuid import UUID

from pony.orm import ObjectNotFound

from core import logger, LiveGameRoom, get_live_game_room
from core.repositories import get_adjacent_boxes, get_adj_special_box, is_trap, find_player_by_id_and_game_id, \
    update_current_position, find_player_by_id, get_card_info_by_id, find_four_traps, set_loser, enter_enclosure
from core.schemas import Movement, RollDice, PlayerBox, GamePlayer, BasicGameInput, DataRoll
from core.exceptions import MysteryException
from core.services.game_service import is_valid_game_player_service


def find_possible_movements(depth: int, current_position: int, exclude: int):
    result = {current_position}
    if depth > 0:
        adjacent_boxes = get_adjacent_boxes(current_position, exclude)
        special = get_adj_special_box(current_position)
        if special:
            result.add(special)
            for adj in get_adjacent_boxes(special, special):
                adjacent_boxes.add(adj)

        for box in adjacent_boxes:
            result.add(box)
            if not is_trap(box):
                others = find_possible_movements(depth - 1, box, current_position)
                for o in others:
                    result.add(o)
    return result


def get_possible_movement(dice_number: int, position: int):
    result = set()
    if is_trap(position):
        traps = find_four_traps()
        for t in traps:
            result_in_trap = find_possible_movements(dice_number, t, -1)
            for b in result_in_trap:
                result.add(b)
        for t in traps:
            result.discard(t)
    else:
        result = find_possible_movements(dice_number, position, -1)
        result.discard(position)
    return result


def find_player_by_id_game_id_service(player_id: UUID, game_id: UUID):
    try:
        return find_player_by_id_and_game_id(player_id, game_id)
    except ObjectNotFound:
        raise MysteryException(message="Game not found!", status_code=404)


async def move_player_service(movement: Movement):
    game_player: GamePlayer = find_player_by_id_game_id_service(movement.player_id, movement.game_id)
    if not game_player.game.started:
        raise MysteryException(message="Game not started!", status_code=400)
    if game_player.game.turn != game_player.player.order:
        raise MysteryException(message="Invalid turn player!", status_code=400)
    if not game_player.player.current_position:
        raise MysteryException(message="Player needs to exit from enclosure first!", status_code=400)
    possible_movement = get_possible_movement(movement.dice_value, game_player.player.current_position.id)
    if movement.next_box_id not in possible_movement:
        raise MysteryException(message="Invalid movement!", status_code=400)
    new_player_position = update_current_position(movement.player_id, movement.next_box_id)
    game_player.player = new_player_position
    room: LiveGameRoom = get_live_game_room(movement.game_id)
    await room.broadcast_json_message("PLAYER_NEW_POSITION", json.loads(game_player.json()))
    return game_player


def valid_card(card_type, id):
    card = get_card_info_by_id(id)
    if card.type != card_type:
        raise MysteryException(message="card is not a ${type}!", status_code=400)


def find_player_pos_service(player_id):
    try:
        player = find_player_by_id(player_id)
    except ObjectNotFound:
        raise MysteryException(message="Player not found", status_code=404)
    position_box = player.current_position
    box = position_box.id
    return box


def set_loser_service(player_id):
    set_loser(player_id)


async def roll_dice_service(roll: RollDice):
    logger.info(roll)
    pos = find_player_pos_service(roll.player_id)
    possible_boxes = get_possible_movement(roll.dice, pos)
    room: LiveGameRoom = get_live_game_room(roll.game_id)
    data = DataRoll(game_id=roll.game_id, player_id=roll.player_id, dice=roll.dice)
    await room.broadcast_json_message("VALUE_DICE", json.loads(data.json()))
    return possible_boxes


def box_enclosure_enter(current_position):
    return current_position and current_position.attribute in ["ENCLOSURE_DOWN", "ENCLOSURE_UP"]


async def enclosure_enter_service(player_game: BasicGameInput):
    logger.info(player_game)
    is_valid_game_player_service(player_game.game_id, player_game.player_id)
    try:
        return enter_enclosure(player_game.player_id)
    except AssertionError:
        raise MysteryException(message="Invalid movement", status_code=400)


async def enclosure_exit_service(player_game: PlayerBox):
    logger.info(player_game)
    return find_player_by_id_game_id_service(player_game.player_id, player_game.game_id)
