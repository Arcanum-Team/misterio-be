from typing import List, Dict

from pony.orm import db_session, select
from core.settings import logger
from core.models.board_model import *
from core.schemas.board_schema import BoardOutput, BoxOutput, EnclosureOutput, RowOutput

a = [[], [], [], []]
a[0].extend([[0, "ENTER", 0, "NONE"], [4, "ENTRY_ENCLOSURE", 15, "DOWN"],
             [10, "ENTRY_ENCLOSURE", 13, "UP"], [15, "ENTRY_ENCLOSURE", 16, "DOWN"]
                , [19, "ENTER", 0, "NONE"]])
a[1].extend([[20, "ENTER", 0, "NONE"], [22, "ENTRY_ENCLOSURE", 12, "LEFT"],
             [30, "ENTRY_ENCLOSURE", 15, "DOWN"], [35, "ENTRY_ENCLOSURE", 17, "LEFT"]
                , [39, "ENTER", 0, "NONE"]])
a[2].extend([[40, "ENTER", 0, "NONE"], [44, "ENTRY_ENCLOSURE", 14, "RIGHT"],
             [50, "ENTRY_ENCLOSURE", 16, "UP"], [56, "ENTRY_ENCLOSURE", 19, "RIGHT"]
                , [59, "ENTER", 0, "NONE"]])
a[3].extend([[60, "ENTER", 0, "NONE"], [63, "ENTRY_ENCLOSURE", 15, "UP"],
             [70, "ENTRY_ENCLOSURE", 18, "DOWN"], [76, "ENTRY_ENCLOSURE", 16, "UP"]
                , [79, "ENTER", 0, "NONE"]])


@db_session
def create_board():
    iterador = 0
    Enclosure(id=12, name="COCHERA")
    Enclosure(id=13, name="ALCOBA")
    Enclosure(id=14, name="BIBLIOTECA")
    Enclosure(id=15, name="VESTIBULO")
    Enclosure(id=16, name="PANTEON")
    Enclosure(id=17, name="BODEGA")
    Enclosure(id=18, name="SALON")
    Enclosure(id=19, name="LABORATORIO")
    for i in range(4):
        for j in range(20):
            new_box_id = i * 20 + j
            if (a[i][iterador][0] == i * 20 + j):
                box_id = a[i][iterador][0]
                box_attr = a[i][iterador][1]
                en_id = a[i][iterador][2]
                box_arrow = a[i][iterador][3]
                logger.info(str(en_id) + str(box_id))
                if en_id < 20 and en_id > 11:
                    Box(id=box_id, row=(i + 1), attribute=box_attr,
                        enclosure_id=Enclosure[en_id], arrow=box_arrow)
                else:
                    Box(id=box_id, row=(i + 1), attribute=box_attr, arrow=box_arrow)
                iterador = (iterador + 1) % 5
            else:
                if ((i == 0 or i == 3) and (j == 6 or j == 13)):
                    if (j == 6):
                        row = 1
                    else:
                        row = 2
                    Box(id=new_box_id, row=(i + 1), row_id=row)
                elif ((i == 1 or i == 2) and (j == 6 or j == 13)):
                    if (j == 6):
                        row = 0
                    else:
                        row = 3
                    Box(id=new_box_id, row=(i + 1), row_id=row)
                else:
                    Box(id=new_box_id, row=(i + 1))
    return select(c for c in Box)[:]


@db_session
def get_complete_board():
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
def get_adjacent_boxes(id: int):
    box: Box = get_box_by_id(id)
    result: List[int] = list()
    for adj in box.adjacent_boxes:
        result.append(adj.adj_box_id)
    return result


@db_session
def get_complete_row(row_id: int):
    result: Set(Box) = Box.select(row=row_id).sort_by(Box.id)
    output: List[BoxOutput] = list()
    position: int = 1
    for b in result:
        box_output: BoxOutput = BoxOutput(id=b.id, position=position, row=b.row, attribute=b.type.value)
        if b.enclosure:
            exits: List[BoxOutput] = list()
            for d in b.enclosure.doors:
                exits.append(BoxOutput(id=d.id, row=d.row, attribute=d.type.value))
            enclosure_output: EnclosureOutput = EnclosureOutput(id=b.enclosure.id, name=b.enclosure.value)
            enclosure_output.doors = exits
            box_output.enclosure = enclosure_output

        if b.related_box:
            box_output.id = b.related_box
        output.append(box_output)
        position = position + 1
    output.sort(key=lambda row: row.position)
    return output


def get_board():
    result: List[RowOutput] = list()
    for i in range(1, 5):
        result.append(RowOutput(id=i, boxes=get_complete_row(i)))

    return result
