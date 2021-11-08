from typing import Dict, List
from pony.orm import db_session, select
from core.models.card_model import Card

cards: Dict[str,List[str]] = { 
    "ENCLOSURE": ["GARAGE", "BEDROOM", "LIBRARY", "LOBBY", "PANTHEON", "CELLAR", 
        "LIVING_ROOM", "LABORATORY"],#8

    "MONSTER": ["DRACULA", "FRANKENSTEIN", "HOMBRE LOBO", "FANTASMA",
        "MOMIA","DR.JEKYLL MR.HYDE"],#14
    
    "VICTIM": ["CONDE", "CONDESA", "AMA DE LLAVES","MOYORDOMO", "DONCELLA", "JARDINERO"]#20
}

@db_session
def initialize_cards():
    if(not Card.select()):
        i = 1
        for key, value in cards.items():
            for v in value:
                Card(id=i, name=v, type=key)
                i = i+1

