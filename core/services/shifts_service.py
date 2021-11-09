from core.repositories import get_adjacent_boxes, find_player_by_id_and_game_id, get_adj_special_box, is_trap
from core.repositories.board_repository import find_four_traps
from core.schemas import Movement, GameOutput, PlayerOutput
from core.exceptions import MysteryException
from core.repositories.card_repository import get_card_info_by_id
from core.services.game_service import get_valid_game


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
    player: PlayerOutput = find_player_by_id_and_game_id(movement.player_id, movement.game_id)
    return get_possible_movement(movement.dice_value, player.current_position.id)


def valid_card(card_type, id):
    card = get_card_info_by_id(id)
    if card.type != card_type:
        raise MysteryException(message="card is not a ${type}!", status_code=400)
