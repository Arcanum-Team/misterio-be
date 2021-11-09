from typing import Set

from pony.orm.core import ObjectNotFound, db_session
from core.exceptions import MysteryException
from core.models import Card
from core.repositories import get_card_by_id, get_cards, get_cards_by_player_id
from core.schemas.card_schema import CardBasicInfo


def get_cards_by_player(player_id):
    try:
        return get_cards_by_player_id(player_id)
    except ObjectNotFound:
        raise MysteryException(message="Player Not Found!", status_code=404)


def get_card_by_id_service(card_id):
    try:
        return get_card_by_id(card_id)
    except ObjectNotFound:
        raise MysteryException(message="Card doesn't exists", status_code=404)


@db_session
def get_all_cards():
    cards: Set[Card] = get_cards()
    return [CardBasicInfo(id=c.id, name=c.name, type=c.type) for c in cards]
