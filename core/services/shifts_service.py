from core.repositories import get_adjacent_boxes
from core.schemas import Movement
from core.exceptions import MysteryException
from core.repositories.card_repository import get_card_info_by_id
from core.services.game_service import get_valid_game


def find_possible_movements(depth: int, current_position: int, exclude: int):
    result = set()
    if depth > 0:
        adjacent_boxes = get_adjacent_boxes(current_position, exclude)
        for box in adjacent_boxes:
            result.add(box)
            others = find_possible_movements(depth - 1, box, current_position)
            for o in others:
                result.add(o)
    return result


def get_possible_movement(dice_number: int, position: int):
    result = find_possible_movements(dice_number, position, -1)
    result.discard(position)
    return result


def move_player_service(movement: Movement):
    return get_valid_game(movement.player_id, movement.game_id)


def valid_card(card_type, id):
    card = get_card_info_by_id(id)
    if card.type != card_type:
        raise MysteryException(message="card is not a ${type}!", status_code=400)
