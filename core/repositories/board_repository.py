from typing import List

from pony.orm import db_session
from core.models.board_model import *
from core.schemas.board_schema import BoxOutput, EnclosureOutput


@db_session
def get_all_boxes():
    return Box.select()


@db_session
def get_box_by_id(id: int):
    return Box[id]


@db_session
def get_enclosure_by_id(id: int):
    return Enclosure[id]


@db_session
def get_box_type_by_id(id: int):
    return BoxType[id]


def is_special_box(value):
    return value in ["COBRA", "SCORPION", "BAT", "SPIDER"]


@db_session
def get_adj_special_box(box_id: int):
    box: Box = get_box_by_id(box_id)
    if is_special_box(box.type.value):
        return next(filter(lambda b: b.id != box_id, box.type.boxes)).id
    return None


@db_session
def is_trap(box_id: int):
    return get_box_by_id(box_id).type.value == "TRAP"


@db_session
def find_four_traps():
    box_type: BoxType = BoxType.get(value="TRAP")
    return [b.id for b in filter(lambda v: v.adjacent_boxes, box_type.boxes)]


@db_session
def get_adjacent_boxes(id: int, exclude: int):
    box: Box = get_box_by_id(id)
    result = set()
    for adj in box.adjacent_boxes:
        result.add(adj.adj_box_id)
    if exclude > 0:
        filter(lambda v: v != exclude, result)
    return result


@db_session
def get_complete_row(row_id: int):
    result: Set(Box) = Box.select(row=row_id).sort_by(Box.id)
    output: List[BoxOutput] = list()
    position: int = 1
    for b in result:
        box_output: BoxOutput = BoxOutput(id=b.id, position=position, attribute=b.type.value)
        if b.enclosure:
            exits: List[BoxOutput] = list()
            for d in b.enclosure.doors:
                exits.append(BoxOutput(id=d.id, attribute=d.type.value))
            enclosure_output: EnclosureOutput = EnclosureOutput(id=b.enclosure.id, name=b.enclosure.value)
            enclosure_output.doors = exits
            box_output.enclosure = enclosure_output

        if b.related_box:
            box_output.id = b.related_box
        output.append(box_output)
        position = position + 1
    output.sort(key=lambda row: row.position)
    return output


@db_session
def get_boxes_by_type(value_type: str):
    return Box.select(type=BoxType.get(value=value_type))


