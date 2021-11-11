from pony.orm import db_session

<<<<<<< HEAD
=======
from core.models.card_model import Card
from core.schemas.card_schema import CardBasicInfo


@db_session
def get_cards():
    return Card.select().sort_by(Card.id)


>>>>>>> af90769ba4f782fd9fa1e1e5a64830814a3170ae
@db_session
def get_card_info_by_id(card_id):
    card = get_card_by_id(card_id)
    return CardBasicInfo(id=card.id, name=card.name, type=card.type)


@db_session
<<<<<<< HEAD
def get_card_info_by_id(card_id):
    c = Card.get(id = card_id)
    return (c.id, c.name, c.type)

@db_session
def get_card(card_id):
    return Card[card_id]
=======
def get_card_by_id(card_id):
    return Card[card_id]
>>>>>>> af90769ba4f782fd9fa1e1e5a64830814a3170ae
