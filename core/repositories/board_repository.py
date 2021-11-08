from typing import List

from pony.orm import db_session
from core.models.board_model import *
from core.schemas.board_schema import BoxOutput, EnclosureOutput, RowOutput


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
