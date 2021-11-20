import json
from logging import Logger

from uuid import UUID

from pony.orm import ObjectNotFound

from core import logger, LiveGameRoom, get_live_game_room
from core.repositories import get_adjacent_boxes, get_adj_special_box, is_trap, find_player_by_id_and_game_id, \
    update_current_position, find_player_by_id, get_card_info_by_id, find_four_traps, set_loser, enter_enclosure, \
    find_game_by_id, find_player_by_turn, get_game_players_count, exit_enclosure, pass_shift, \
    find_player_enclosure, is_player_card
from core.schemas import Movement, RollDice, PlayerBox, GamePlayer, DataRoll, Acusse, \
    DataSuspectNotice, SuspectResponse, DataSuspectResponse, Suspect, DataAccuse
from core.exceptions import MysteryException
from core.services import valid_is_started, is_valid_game_player_service, get_envelop, valid_is_started
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
    

def valid_cards(accuse: Acusse):
    valid_card("ENCLOSURE", accuse.enclosure_id)
    valid_card("MONSTER", accuse.monster_id)
    valid_card("VICTIM", accuse.victim_id)


def valid_cards_suspect(suspect: Suspect):
    valid_card("MONSTER", suspect.monster_id)
    valid_card("VICTIM", suspect.victim_id)


def get_player_reached(game_id, suspect_cards):
    game = find_game_by_id(game_id)
    players_len = get_game_players_count(game_id)
    player_turn = game.turn
    reached_player = None
    for i in range(0, players_len - 1):
        p_id, p_cards = find_player_by_turn(game_id, ((player_turn + i % players_len) + 1))
        if {} != set(p_cards).intersection(suspect_cards):
            reached_player = p_id
        logger.info(p_cards)

    return reached_player


async def suspect_service(suspect: Suspect):
    is_valid_game_player_service(suspect.game_id, suspect.player_id)
    valid_cards_suspect(suspect)
    valid_is_started(suspect.game_id)
    enclosure_id = valid_player_enclosure(suspect.player_id)
    suspect_cards = [enclosure_id, suspect.monster_id, suspect.victim_id]
    player_id = get_player_reached(suspect.game_id, suspect_cards)
    room: LiveGameRoom = get_live_game_room(suspect.game_id)
    data = DataSuspectNotice(player_id=suspect.player_id, reached_player_id=player_id,
                             enclosure_id=enclosure_id, monster_id=suspect.monster_id,
                             victim_id=suspect.victim_id, game_id=suspect.game_id)
    await room.broadcast_json_message("SUSPECT", json.loads(data.json()))


async def suspect_response_service(response: SuspectResponse):
    is_valid_game_player_service(response.game_id, response.from_player)
    is_valid_game_player_service(response.game_id, response.to_player)
    valid_is_player_card(response.from_player, response.card)
    room: LiveGameRoom = get_live_game_room(response.game_id)
    data = DataSuspectResponse(card=response.card)
    await room.message_to_player(response.to_player, "SUSPECT_RESPONSE", json.loads(data.json()))
    return "SUSPECT_RESPONSE_SENDED"


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
    is_valid_game_player_service(player_game.game_id, player_game.player_id)
    try:
        game_player: GamePlayer = exit_enclosure(player_game.player_id, player_game.box_id)
        room: LiveGameRoom = get_live_game_room(player_game.game_id)
        await room.broadcast_json_message("ENCLOSURE_EXIT", json.loads(game_player.json()))
        return game_player
    except AssertionError:
        raise MysteryException(message="Invalid movement", status_code=400)


async def pass_turn_service(player_game: BasicGameInput):
    logger.info(player_game)
    is_valid_game_player_service(player_game.game_id, player_game.player_id)
    try:
        game_player: GamePlayer = pass_shift(player_game.player_id)
        room: LiveGameRoom = get_live_game_room(player_game.game_id)
        await room.broadcast_json_message("ASSIGN_SHIFT", json.loads(game_player.json()))
    except AssertionError:
        raise MysteryException(message="Invalid movement", status_code=400)


async def accuse_service(accuse: Acusse):
    valid_cards(accuse)
    valid_is_started(accuse.game_id)
    is_valid_game_player_service(accuse.game_id, accuse.player_id)
    envelope = get_envelop(accuse.game_id)
    logger.info(envelope)
    accuse_cards = [accuse.enclosure_id, accuse.monster_id, accuse.victim_id]
    player_id = accuse.player_id
    r = set(envelope).difference(accuse_cards)
    if len(r) == 0:
        data = DataAccuse(player_id=player_id, result=True, cards=envelope,
        game_id=accuse.game_id)
    else:
        data = DataAccuse(player_id=player_id, result=False, cards=accuse_cards, 
        game_id=accuse.game_id)
        set_loser(player_id)

    wb = get_live_game_room(accuse.game_id)
    await wb.broadcast_json_message("ACCUSE", json.loads(data.json()))
    return data


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
        raise MysteryException(message="The player is not showing a card of her own")