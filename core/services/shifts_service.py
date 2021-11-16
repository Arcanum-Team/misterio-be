from pony.orm import ObjectNotFound

from core.repositories import get_adjacent_boxes, get_adj_special_box, is_trap, find_player_by_id_and_game_id, \
    update_current_position, find_player_by_id, get_card_info_by_id, find_four_traps, set_loser, \
    find_game_by_id, find_player_by_turn
from core.schemas import Movement, PlayerOutput, Acusse
from core.exceptions import MysteryException


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


def move_player_service(movement: Movement):
    try:
        player: PlayerOutput = find_player_by_id_and_game_id(movement.player_id, movement.game_id)
        possible_movement = get_possible_movement(movement.dice_value, player.current_position.id)
        if movement.next_box_id not in possible_movement:
            raise MysteryException(message="Invalid movement!", status_code=400)
        # TODO send websocket message new player position
        return update_current_position(movement.player_id, movement.next_box_id)
    except ObjectNotFound:
        raise MysteryException(message="Game not found!", status_code=404)


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

def validCards(accuse: Acusse):
    valid_card("ENCLOSURE", accuse.enclosure_id)
    valid_card("MONSTER", accuse.monster_id)
    valid_card("VICTIM", accuse.victim_id)

def get_player_reached(game_id, suspect_cards):
    game = find_game_by_id(game_id)
    player_turn = game.turn 
    reached_player = None
    l = len(game.players)
    for i in range(0, l-1):
        player = find_player_by_turn((player_turn + i % l) + 1)
        cards = list(map(lambda c:c.id, player.cards))
        if {} == set(cards).difference(suspect_cards):
            reached_player = player

    return reached_player