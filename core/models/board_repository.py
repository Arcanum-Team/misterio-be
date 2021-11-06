from logging import log
from typing import NoReturn
from uuid import UUID
from pony.orm import db_session, select, ObjectNotFound
from core.settings import logger
from core.models.board_model import *
from core.schemas.board_schema import BoardOutput, BoxOutput, EnclosureOutput, RowOutput
import numpy as np

a = [[],[],[],[]]
a[0].extend([[0,"ENTER",0,"NONE"],[4,"ENTRY_ENCLOSURE", 15, "DOWN"],
 [10,"ENTRY_ENCLOSURE", 13, "UP"], [15,"ENTRY_ENCLOSURE", 16, "DOWN"]
 ,[19,"ENTER",0,"NONE"]])
a[1].extend([[20,"ENTER",0,"NONE"], [22,"ENTRY_ENCLOSURE", 12, "LEFT"],
 [30,"ENTRY_ENCLOSURE", 15, "DOWN"], [35,"ENTRY_ENCLOSURE", 17, "LEFT"]
 ,[39,"ENTER",0,"NONE"]])
a[2].extend([[40,"ENTER",0,"NONE"], [44,"ENTRY_ENCLOSURE", 14, "RIGHT"], 
  [50,"ENTRY_ENCLOSURE", 16, "UP"], [56,"ENTRY_ENCLOSURE", 19, "RIGHT"]
  ,[59,"ENTER",0,"NONE"]])
a[3].extend([[60,"ENTER",0,"NONE"], [63,"ENTRY_ENCLOSURE", 15, "UP"], 
  [70,"ENTRY_ENCLOSURE", 18, "DOWN"], [76,"ENTRY_ENCLOSURE", 16, "UP"]
  ,[79,"ENTER",0,"NONE"]])

@db_session
def create_board():
    iterador = 0
    Enclosure(id=12,name="COCHERA")
    Enclosure(id=13,name="ALCOBA")
    Enclosure(id=14,name="BIBLIOTECA")
    Enclosure(id=15,name="VESTIBULO")
    Enclosure(id=16,name="PANTEON")
    Enclosure(id=17,name="BODEGA")
    Enclosure(id=18,name="SALON")
    Enclosure(id=19,name="LABORATORIO")
    for i in range(4):
        for j in range(20):
            new_box_id = i*20 + j
            if(a[i][iterador][0] == i*20+j):
                box_id = a[i][iterador][0]
                box_attr = a[i][iterador][1]
                en_id = a[i][iterador][2]
                box_arrow = a[i][iterador][3]
                logger.info(str(en_id) + str(box_id))
                if en_id < 20 and en_id > 11:
                    Box(id=box_id, row=(i+1), attribute=box_attr,
                        enclosure_id=Enclosure[en_id], arrow=box_arrow)
                else:
                    Box(id=box_id, row=(i+1), attribute=box_attr, arrow=box_arrow)
                iterador = (iterador + 1)%5                  
            else:
                if((i == 0 or i == 3) and (j == 6 or j == 13)):
                    if(j==6):
                        row = 1
                    else:
                        row = 2
                    Box(id= new_box_id ,row=(i+1),row_id=row)
                elif((i == 1 or i == 2) and (j == 6 or j == 13)):
                    if(j==6):
                        row = 0
                    else:
                        row = 3
                    Box(id= new_box_id ,row=(i+1),row_id=row)
                else: 
                    Box(id= new_box_id ,row=(i+1))
    return select(c for c in Box)[:]


@db_session
def get_board(): 
    a = select(c for c in Box)[:]
    if(not a):
        a = create_board()
    boxes = []
    for c in a:
        if not c.enclosure_id:
            box = BoxOutput(position=c.id, row=c.row, attribute=c.attribute,
             arrow= c.arrow, row_id = c.row_id)    
        else:
            box = BoxOutput(position=c.id, row=c.row, attribute=c.attribute,
             enclosure_id= c.enclosure_id.id, arrow= c.arrow, row_id = c.row_id)
        boxes.append(box)
    rows = []
    for i in range(1,5):
        bs = filter(lambda b: b.row == i, boxes)
        rows.append(RowOutput(position=i, boxes=list(bs)))
    
    enclosuresRes = []
    enclosures = select(e for e in Enclosure)[:]
    for r in enclosures:
        ds = filter(lambda d: d.enclosure_id == r.id, boxes)
        enclosuresRes.append(EnclosureOutput(id=r.id, name=r.name, doors=list(ds)))
    res = BoardOutput(rows=rows,enclosures=enclosuresRes)
    return res