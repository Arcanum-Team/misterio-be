from uuid import UUID
from pony.orm import db_session, select, ObjectNotFound
from core import logger
from core.exceptions import MysteryException

from core.models.card_model import Card
from core.settings import logger
from core.models.player_repository import find_player_by_id
from core.models.games_repository import find_game_by_id

cards = [ #monsters
         ["DRACULA", "MONSTER"],["FRANKENSTEIN", "MONSTER"],["HOMBRE_LOBO", "MONSTER"], 
         ["FANTASMA", "MONSTER"], ["MOMIA", "MONSTER"], ["DR.JEKYLL_MR.HYDE", "MONSTER"],
          #victims
         ["CONDE","VICTIM"], ["CONDESA","VICTIM"], ["AMA_DE_LLAVES","VICTIM"], 
         ["MOYORDOMO","VICTIM"], ["DONCELLA","VICTIM"], ["JARDINERO", "VICTIM"],
          #enclosures
         ["COCHERA", "ENCLOSURE"], ["ALCOBA", "ENCLOSURE"] ,["BIBLIOTECA", "ENCLOSURE"],
         ["VESTIBULO", "ENCLOSURE"], ["PANTEON", "ENCLOSURE"], ["BODEGA", "ENCLOSURE"],
         ["SALON", "ENCLOSURE"], ["LABORATORIO", "ENCLOSURE"]
        ]

@db_session
def initializeCards():
    for i in range(len(cards)):
        Card(id=i, name=cards[i][0] , type=cards[i][1])

@db_session
def get_cards():
    return select((c.id, c.name, c.type) for c in Card)[:]

@db_session
def get_cards_by_player_id(id_player):
    player_by_id= find_player_by_id(id_player)
    if (not player_by_id.cards):
            raise MysteryException(message="This player doesn't have any cards assigned yet!", status_code=400)
    return player_by_id.cards

@db_session
def get_card_info_by_id(card_id):
    return select((c.id, c.name, c.type) for c in Card
        if c.id==card_id)[:]


