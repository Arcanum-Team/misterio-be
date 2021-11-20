from pony.orm import db_session
import random

from core.models.card_model import Card
from core.schemas.card_schema import CardBasicInfo
from core.repositories.player_repository import find_player_by_id
from core.models.players_model import Player
from core.models.games_model import Game

@db_session
def get_cards():
    return Card.select().sort_by(Card.id)


@db_session
def get_card_info_by_id(card_id):
    card = get_card_by_id(card_id)
    return CardBasicInfo(id=card.id, name=card.name, type=card.type)


@db_session
def get_card_by_id(card_id):
    return Card[card_id]

@db_session
def witch(player_id):
    player: Player = find_player_by_id(player_id)
    got_the_witch= False
    for card in player.cards:
        if card.type=="WITCH":
            got_the_witch= True
            player.cards.remove(card)
            break
    if got_the_witch:
        game: Game= player.game
        card = get_card_by_id(random.choice(game.envelop))
        return CardBasicInfo(id=card.id, name=card.name, type=card.type)
    return False

