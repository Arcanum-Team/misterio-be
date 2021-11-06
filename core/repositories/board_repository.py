from pony.orm import db_session, select
from core.models.board_model import *
from core.schemas.board_schema import BoxOutput, RowOutput

{
    "id": 12,
    "name": "COCHERA",
    "id": 13,
    "name": "ALCOBA",
    "id": 14,
    "name": "BIBLIOTECA",
    "id": 15,
    "name": "VESTIBULO",
    "id": 16,
    "name": "PANTEON",
    "id": 17,
    "name": "BODEGA",
    "id": 18,
    "name": "SALON",
    "id": 19,
    "name": "LABORATORIO",
}

a = [[], [], [], []]
a[0].extend([[0, "ENTER", 0, "NONE"], [19, "ENTER", 0, "NONE"],
             [4, "ENTRY_ENCLOSURE", 15, "DOWN"], [10, "ENTRY_ENCLOSURE", 13, "UP"],
             [15, "ENTRY_ENCLOSURE", 16, "DOWN"]])
a[1].extend([[20, "ENTER", 0, "NONE"], [39, "ENTER", 0, "NONE"],
             [22, "ENTRY_ENCLOSURE", 12, "LEFT"], [30, "ENTRY_ENCLOSURE", 15, "LEFT"],
             [35, "ENTRY_ENCLOSURE", 17, "LEFT"]])
a[2].extend([[40, "ENTER", 0, "NONE"], [59, "ENTER", 0, "NONE"],
             [44, "ENTRY_ENCLOSURE", 14, "RIGHT"], [50, "ENTRY_ENCLOSURE", 16, "RIGHT"],
             [56, "ENTRY_ENCLOSURE", 19, "RIGHT"]])
a[3].extend([[60, "ENTER", 0, "NONE"], [79, "ENTER", 0, "NONE"],
             [63, "ENTRY_ENCLOSURE", 15, "UP"], [70, "ENTRY_ENCLOSURE", 18, "DOWN"],
             [76, "ENTRY_ENCLOSURE", 16, "UP"]])


@db_session
def create_board():
    iterador = 0
    for i in range(4):
        for j in range(20):
            if (a[i][iterador][0] == j):
                Box(id=j, row=(i + 1), attribute=a[i][iterador][1],
                    enclosure_id=a[i][iterador][2], arrow=a[i][iterador][3])
                iterador = iterador + 1
            else:
                Box(id=i * 20 + j, row=(i + 1))
    return select(c for c in Box)[:]


@db_session
def get_board():
    a = select(c for c in Box)[:]
    if (not a):
        a = create_board()
    boxes = []
    for c in a:
        boxes.append(
            BoxOutput(position=c.id, row=c.row, attribute=c.attribute,
                      enclosure_id=c.enclosure_id, arrow=c.arrow, row_id=c.row_id)
        )
    res = []
    for i in range(1, 5):
        bs = filter(lambda b: b.row == i, boxes)
        res.append(RowOutput(position=i, boxes=list(bs)))

    return res
