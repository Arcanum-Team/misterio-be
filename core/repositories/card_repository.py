from pony.orm import db_session, select
from core.models.card_model import Card

cards = [  # monsters
    ["DRACULA", "MONSTER"], ["FRANKENSTEIN", "MONSTER"], ["HOMBRE LOBO", "MONSTER"],
    ["FANTASMA", "MONSTER"], ["MOMIA", "MONSTER"], ["DR.JEKYLL MR.HYDE", "MONSTER"],#5
    # victims
    ["CONDE", "VICTIM"], ["CONDESA", "VICTIM"], ["AMA DE LLAVES", "VICTIM"],
    ["MOYORDOMO", "VICTIM"], ["DONCELLA", "VICTIM"], ["JARDINERO", "VICTIM"],#11
    # enclosures
    ["COCHERA", "ENCLOSURE"], ["ALCOBA", "ENCLOSURE"], ["BIBLIOTECA", "ENCLOSURE"],
    ["VESTIBULO", "ENCLOSURE"], ["PANTEON", "ENCLOSURE"], ["BODEGA", "ENCLOSURE"],
    ["SALON", "ENCLOSURE"], ["LABORATORIO", "ENCLOSURE"] #19
]


@db_session
def initialize_cards():
    for i in range(len(cards)):
        Card(id=i, name=cards[i][0], type=cards[i][1])


@db_session
def get_cards():
    return select((c.id, c.name, c.type) for c in Card)[:]


@db_session
def get_card_info_by_id(card_id):
    return select((c.id, c.name, c.type) for c in Card
                  if c.id == card_id)[:]
