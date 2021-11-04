from uuid import UUID
import random
from pony.orm import db_session, select, ObjectNotFound
from core import logger
from core.exceptions import MysteryException

from core.models.card_model import Card
from core.models.games_model import Game
from core.settings import logger
from core.models.player_repository import find_player_by_id
from core.models.card_model import Mistery


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
def cards_assignment(game_id):
   cards_id_list=list(range(21))
   random_mistery_monster=random.randint(0, 5)
   random_mistery_victim=random.randint(6, 11)
   random_mistery_enclosure=random.randint(12, 19)
   Mistery(game_id=game_id, mistery_monster=random_mistery_monster, mistery_victim=random_mistery_victim, mistery_enclosure=random_mistery_enclosure)
   cards_id_list.remove(random_mistery_monster)
   cards_id_list.remove(random_mistery_victim)
   cards_id_list.remove(random_mistery_enclosure)
   
   g= Game[game_id]
   cards_by_player=int(18/len(g.players))
   for i in g.players:
       for j in range(cards_by_player):
           random_card=random.choice(cards_id_list)
           if (random_card==20):
               i.witch= True
           else:
               i.cards.append(random_card)
           cards_id_list.remove(random_card)


@db_session
def get_cards_by_player_id(player_id):
    player_by_id= find_player_by_id(player_id)
    if (not player_by_id.cards):
            raise MysteryException(message="This player doesn't have any cards assigned yet!", status_code=400)
    return player_by_id.cards

@db_session
def get_card_info_by_id(card_id):
    return select((c.id, c.name, c.type) for c in Card
        if c.id==card_id)[:]


