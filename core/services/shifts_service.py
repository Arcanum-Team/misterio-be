import json

from uuid import UUID

from pony.orm import ObjectNotFound

from core import logger, LiveGameRoom, get_live_game_room
from core.repositories import get_adjacent_boxes, get_adj_special_box, is_trap, find_player_by_id_and_game_id, \
    update_current_position, find_player_by_id, get_card_info_by_id, find_four_traps, enter_enclosure, \
    exit_enclosure, pass_shift, \
    find_player_enclosure, is_player_card, do_suspect, do_accuse, execute_witch
from core.schemas import Movement, RollDice, PlayerBox, GamePlayer, DataRoll, Acusse, SuspectResponse, \
    DataSuspectResponse, Suspect
from core.exceptions import MysteryException
from core.services import is_valid_game_player_service
from core.schemas.player_schema import BasicGameInput


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
    if room:
        await room.broadcast_json_message("PLAYER_NEW_POSITION", json.loads(game_player.json()))
    else:
        logger.error("Web socket message not sent!")
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


def valid_cards(accuse: Acusse):
    valid_card("ENCLOSURE", accuse.enclosure_id)
    valid_card("MONSTER", accuse.monster_id)
    valid_card("VICTIM", accuse.victim_id)


def valid_cards_suspect(suspect: Suspect):
    valid_card("MONSTER", suspect.monster_id)
    valid_card("VICTIM", suspect.victim_id)


async def suspect_service(suspect: Suspect):
    valid_cards_suspect(suspect)
    suspect_notice = do_suspect(suspect)
    room: LiveGameRoom = get_live_game_room(suspect.game_id)
    if room:
        await room.broadcast_json_message("SUSPECT", json.loads(suspect_notice.json()))
    else:
        logger.error("Web socket message not sent!")


async def suspect_response_service(response: SuspectResponse):
    is_valid_game_player_service(response.game_id, response.from_player)
    is_valid_game_player_service(response.game_id, response.to_player)
    valid_is_player_card(response.from_player, response.card)
    data = DataSuspectResponse(card=response.card)
    room: LiveGameRoom = get_live_game_room(response.game_id)
    if room:
        await room.message_to_player(response.to_player, "SUSPECT_RESPONSE", json.loads(data.json()))
    else:
        logger.error("Web socket message not sent!")
    return "SUSPECT_RESPONSE_SENT"


async def roll_dice_service(roll: RollDice):
    logger.info(roll)
    pos = find_player_pos_service(roll.player_id)
    possible_boxes = get_possible_movement(roll.dice, pos)
    data = DataRoll(game_id=roll.game_id, player_id=roll.player_id, dice=roll.dice)
    room: LiveGameRoom = get_live_game_room(roll.game_id)
    if room:
        await room.broadcast_json_message("VALUE_DICE", json.loads(data.json()))
    else:
        logger.error("Web socket message not sent!")
    return possible_boxes


def box_enclosure_enter(current_position):
    return current_position and current_position.attribute in ["ENCLOSURE_DOWN", "ENCLOSURE_UP"]


async def enclosure_enter_service(player_game: BasicGameInput):
    logger.info(player_game)
    is_valid_game_player_service(player_game.game_id, player_game.player_id)
    try:
        game_player: GamePlayer = enter_enclosure(player_game.player_id)
        room: LiveGameRoom = get_live_game_room(player_game.game_id)
        if room:
            await room.broadcast_json_message("ENCLOSURE_ENTER", json.loads(game_player.json()))
        else:
            logger.error("Web socket message not sent!")
        return game_player
    except AssertionError:
        raise MysteryException(message="Invalid movement", status_code=400)


async def enclosure_exit_service(player_game: PlayerBox):
    logger.info(player_game)
    is_valid_game_player_service(player_game.game_id, player_game.player_id)
    try:
        game_player: GamePlayer = exit_enclosure(player_game.player_id, player_game.box_id)
        room: LiveGameRoom = get_live_game_room(player_game.game_id)
        if room:
            await room.broadcast_json_message("ENCLOSURE_EXIT", json.loads(game_player.json()))
        else:
            logger.error("Web socket message not sent!")
        return game_player
    except AssertionError:
        raise MysteryException(message="Invalid movement", status_code=400)


async def pass_turn_service(player_game: BasicGameInput):
    logger.info(player_game)
    try:
        game_player: GamePlayer = pass_shift(player_game.game_id, player_game.player_id)
        room: LiveGameRoom = get_live_game_room(player_game.game_id)
        if room:
            await room.broadcast_json_message("ASSIGN_SHIFT", json.loads(game_player.json()))
        else:
            logger.error("Web socket message not sent!")
    except AssertionError:
        raise MysteryException(message="Invalid movement", status_code=400)


async def accuse_service(accuse: Acusse):
    valid_cards(accuse)
    data_accuse = do_accuse(accuse)
    room = get_live_game_room(accuse.game_id)
    if room:
        await room.broadcast_json_message("ACCUSE", json.loads(data_accuse.json()))  #
    else:
        logger.error("Web socket message not sent!")
    return data_accuse


def valid_player_enclosure(player_id):
    try:
        enclosure_id = find_player_enclosure(player_id)
        logger.info(enclosure_id)
        return enclosure_id
    except AssertionError:
        raise MysteryException(message="Player is not in enclosure", status_code=400)


def valid_is_player_card(player_id, card_id):
    try:
        is_player_card(player_id, card_id)
    except AssertionError:
        raise MysteryException(message="The player is not showing a card of her own", status_code=400)


async def execute_witch_service(player_game: BasicGameInput):
    logger.info(player_game)
    card = execute_witch(player_game)
    room: LiveGameRoom = get_live_game_room(player_game.game_id)
    if room:
        await room.broadcast_json_message("PLAYER_USE_WITCH_CARD", {"player_id": str(player_game.player_id)})
    else:
        logger.error("Web socket message not sent!")
    return {"card": card}
