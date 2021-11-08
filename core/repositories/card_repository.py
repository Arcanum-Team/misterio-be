from pony.orm import db_session, select
from core.models.card_model import Card


@db_session
def get_cards():
    return select((c.id, c.name, c.type) for c in Card)[:]


@db_session
def get_card_info_by_id(card_id):
    return select((c.id, c.name, c.type) for c in Card
                  if c.id == card_id)[:]
