from pony.orm import db_session
from core.models.card_model import Card


@db_session
def get_cards():
    return Card.select()


@db_session
def get_card_info_by_id(card_id):
    c = Card.get(id=card_id)
    return c.id, c.name, c.type


@db_session
def get_card_by_id(card_id):
    return Card[card_id]
