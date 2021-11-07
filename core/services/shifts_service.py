from typing import List, Set

from core.schemas import Movement, Box


def find_adjacent_boxes(current_position: int, exclude: int):
    return set()


def find_possible_movements(depth: int, current_position: int, exclude: int):
    if depth > 0:
        result: Set[int] = set()
        adjacent_boxes: Set[int] = find_adjacent_boxes(current_position, exclude)
        result.union(adjacent_boxes)
        for box in adjacent_boxes:
            result.union(find_possible_movements(depth - 1, box, current_position))
        return result
    else:
        return set()


def move_player(movement: Movement):
    possible_movements: List[Box] = find_possible_movements()
    pass

