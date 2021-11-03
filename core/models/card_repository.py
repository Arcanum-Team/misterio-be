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
    for c in cards:
        Card(name=c[0] , type=c[1])

@db_session
def get_cards():
    return select((c.id, c.name, c.type) for c in Card)[:]

@db_session
def get_cards_by_player_id(id_player):
    player_by_id= find_player_by_id(id_player)
    if player_by_id.cards:
        return select((c.id, c.name, c.type) for c in player_by_id.cards)[:]
    return "this player does't have any card assigned yet"

@db_session
def get_cards_by_game_id(id_game):
    game_by_id= find_game_by_id(id_game)
    if game_by_id:
        players_id= select(p.id for p in game_by_id.players)[:]
        return [get_cards_by_player_id(id_player) for id_player in players_id]
    return "this game does't exist yet"