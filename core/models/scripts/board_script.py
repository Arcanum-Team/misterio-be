from typing import Dict, List, Optional, Set
from pony.orm import db_session
from pydantic import BaseModel, Required

from core.models import Enclosure, Box, BoxType, BoxAdjacent
from core.repositories import get_all_boxes, get_box_by_id, get_box_type_by_id, get_enclosure_by_id

enclosures: Dict[int, str] = {
    1: "GARAGE",
    2: "BEDROOM",
    3: "LIBRARY",
    4: "LOBBY",
    5: "PANTHEON",
    6: "CELLAR",
    7: "LIVING_ROOM",
    8: "LABORATORY"
}

box_types: Dict[int, str] = {
    1: "NONE",
    2: "ENTRY",
    3: "TRAP",
    4: "ENCLOSURE_UP",
    5: "ENCLOSURE_DOWN"
}


class Cross:

    def __init__(self, row_id: int, related_row_id: int, related_box_id: int) -> None:
        super().__init__()
        self.row_id = row_id
        self.related_row_id = related_row_id
        self.related_box_id = related_box_id


class BoxInput:

    def __init__(self, row_id: int, ids: List[int], enclosure_id: int = None) -> None:
        super().__init__()
        self.row_id = row_id
        self.ids = ids
        self.enclosure_id = enclosure_id


# Key is box_type id
basic_boxes: Dict[int, List[BoxInput]] = {
    1: [
        BoxInput(row_id=1, ids=[2, 3, 4, 6, 8, 9, 10, 12, 13, 15, 17, 18, 19]),
        BoxInput(row_id=2, ids=[22, 24, 25, 26, 28, 29, 30, 32, 33, 35, 37, 38, 39]),
        BoxInput(row_id=3, ids=[42, 43, 44, 46, 48, 49, 50, 52, 53, 55, 56, 58, 59]),
        BoxInput(row_id=4, ids=[62, 63, 65, 66, 68, 69, 70, 72, 73, 75, 76, 78, 79]),
    ],
    2: [
        BoxInput(row_id=1, ids=[1, 20]),
        BoxInput(row_id=2, ids=[21, 40]),
        BoxInput(row_id=3, ids=[41, 60]),
        BoxInput(row_id=4, ids=[61, 80]),
    ],
    4: [
        BoxInput(row_id=1, ids=[11], enclosure_id=2),
        BoxInput(row_id=3, ids=[45], enclosure_id=3),
        BoxInput(row_id=3, ids=[51], enclosure_id=5),
        BoxInput(row_id=3, ids=[57], enclosure_id=8),
        BoxInput(row_id=4, ids=[64], enclosure_id=4),
        BoxInput(row_id=4, ids=[77], enclosure_id=5),
    ],
    5: [
        BoxInput(row_id=1, ids=[5], enclosure_id=4),
        BoxInput(row_id=1, ids=[16], enclosure_id=5),
        BoxInput(row_id=2, ids=[23], enclosure_id=1),
        BoxInput(row_id=2, ids=[31], enclosure_id=4),
        BoxInput(row_id=2, ids=[36], enclosure_id=6),
        BoxInput(row_id=4, ids=[71], enclosure_id=7),
    ]
}

# key: box_id, value: Cross
traps: Dict[int, Cross] = {
    7: Cross(row_id=1, related_row_id=2, related_box_id=27),
    14: Cross(row_id=1, related_row_id=3, related_box_id=47),
    34: Cross(row_id=2, related_row_id=4, related_box_id=67),
    54: Cross(row_id=3, related_row_id=4, related_box_id=74)
}


@db_session
def populate_enclosures():
    for key, value in enclosures.items():
        Enclosure(id=key, value=value)


@db_session
def populate_box_types():
    for key, value in box_types.items():
        BoxType(id=key, value=value)


@db_session
def populate_basic_boxes():
    for key, value in basic_boxes.items():
        box_type: BoxType = get_box_type_by_id(key)
        for bi in value:
            for id in bi.ids:
                box: Box = Box(id=id, row=bi.row_id, type=box_type)
                if bi.enclosure_id:
                    box.enclosure = get_enclosure_by_id(bi.enclosure_id)


@db_session
def populate_traps():
    box_type: BoxType = get_box_type_by_id(3)
    for key, value in traps.items():
        Box(id=key, row=value.row_id, type=box_type)
        Box(id=value.related_box_id, row=value.related_row_id, type=box_type, related_box=key)


@db_session
def board_was_populated():
    return len(get_all_boxes()) > 0


@db_session
def append_adjacent_trap_boxes():
    for key, value in traps.items():
        box: Box = get_box_by_id(key)
        BoxAdjacent(adj_box_id=key - 1, box=box)
        BoxAdjacent(adj_box_id=key + 1, box=box)
        BoxAdjacent(adj_box_id=value.related_box_id - 1, box=box)
        BoxAdjacent(adj_box_id=value.related_box_id + 1, box=box)


def append_adjacent_boxes():
    append_adjacent_basic_boxes()
    append_adjacent_trap_boxes()


@db_session
def append_adjacent_basic_boxes():
    for key, value in basic_boxes.items():
        if key in [1, 4, 5]:
            for bi in value:
                for id in bi.ids:
                    box: Box = get_box_by_id(id)
                    if id not in [26, 46, 66, 73]:
                        BoxAdjacent(adj_box_id=id + 1, box=box)
                    if id not in [28, 48, 68, 75]:
                        BoxAdjacent(adj_box_id=id - 1, box=box)
        else:  # key is 2 (entry)
            for bi in value:
                for id in bi.ids:
                    box: Box = get_box_by_id(id)
                    if id % 2 == 1:
                        BoxAdjacent(adj_box_id=id + 1, box=box)
                    else:
                        BoxAdjacent(adj_box_id=id - 1, box=box)


def populate_board():
    if not board_was_populated():
        populate_enclosures()
        populate_box_types()
        populate_basic_boxes()
        populate_traps()
        append_adjacent_boxes()
