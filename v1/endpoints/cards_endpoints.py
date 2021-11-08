from typing import List
from fastapi import APIRouter
from uuid import UUID
from core.schemas.card_schema import CardBasicInfo
from core.exceptions import MysteryException
from core.repositories import get_card_info_by_id, get_cards, initialize_cards

cards_router = APIRouter()


@cards_router.get("/", response_model=List[CardBasicInfo])
def get_all_cards():
    cards = get_cards()
    if len(cards) == 0:
        initialize_cards()
        cards = get_cards()

    return [CardBasicInfo(id=c[0], name=c[1], type=c[2]) for c in cards]


@cards_router.get("/{id}", response_model=List[CardBasicInfo])
def get_each_player_cards(id: UUID):
    cards_by_player = get_cards_by_player_id(id)
    player_cards_info = []
    for card_id in cards_by_player:
        card_info = get_card_info_by_id(card_id)[0]
        if not card_info:
            raise MysteryException(message="Card without info!", status_code=400)
        player_cards_info.append(card_info)
    return [CardBasicInfo(id=c[0], name=c[1], type=c[2]) for c in player_cards_info]
