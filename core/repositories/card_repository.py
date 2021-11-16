from pony.orm import db_session

from core.models.card_model import Card
from core.schemas.card_schema import CardBasicInfo


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
