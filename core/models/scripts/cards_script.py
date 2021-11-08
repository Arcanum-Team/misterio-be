from typing import Dict, List
from pony.orm import db_session
from core.models.card_model import Card

cards: Dict[str,List[str]] = { 
    "MONSTER": ["DRACULA", "FRANKENSTEIN", "HOMBRE LOBO", "FANTASMA",
        "MOMIA","DR.JEKYLL MR.HYDE"],
    "VICTIM": ["CONDE", "CONDESA", "AMA DE LLAVES","MOYORDOMO", "DONCELLA", "JARDINERO"],

    "ENCLOSURE": ["COCHERA", "ALCOBA", "BIBLIOTECA", "VESTIBULO","PANTEON",
        "BODEGA", "SALON", "LABORATORIO"] 
}

@db_session
def initialize_cards():
    i = 0
    for key, value in cards.items():
        for v in value:
            Card(id=i, name=v, type=key)
            i = i+1

