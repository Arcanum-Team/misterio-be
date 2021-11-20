from typing import Dict, List
from pony.orm import db_session
from core.models.card_model import Card
from core.repositories import get_cards

cards: Dict[str, List[str]] = {
    "ENCLOSURE": ["COCHERA", "ALCOBA", "BIBLIOTECA", "VESTIBULO", "PANTEON", "BODEGA",
                  "SALON", "LABORATORIO"],  # 8

    "MONSTER": ["DRACULA", "FRANKENSTEIN", "HOMBRE LOBO", "FANTASMA",
                "MOMIA", "DR. JEKYLL MR. HYDE"],  # 14

    "VICTIM": ["CONDE", "CONDESA", "AMA DE LLAVES", "MAYORDOMO", "DONCELLA", "JARDINERO"],  # 20
    "WITCH": ["BRUJA"]
}


@db_session
def initialize_cards():
    if len(get_cards()) == 0:
        i = 1
        for key, value in cards.items():
            for v in value:
                Card(id=i, name=v, type=key)
                i = i + 1
