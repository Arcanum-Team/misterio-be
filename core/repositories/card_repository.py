from pony.orm import db_session, select
from core.models.card_model import Card


@db_session
def get_cards():
    return select((c.id, c.name, c.type) for c in Card)[:]


@db_session
def get_card_info_by_id(card_id):
    c = Card.get(id = card_id)
    return (c.id, c.name, c.type)

@db_session
def get_card(card_id):
    return Card[card_id]