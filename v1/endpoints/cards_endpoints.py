from logging import log
from core.settings import logger
from typing import List
from fastapi import APIRouter
from core.schemas.card_schema import CardBasicInfo
from core.exceptions import MysteryException
from core.models.card_repository import get_card_info_by_id, get_cards, initializeCards
from core.models.card_repository import get_cards_by_player_id
from uuid import UUID

cards_router = APIRouter()

@cards_router.get("/", response_model= List[CardBasicInfo])
def get_all_cards():
    cards = get_cards()
    if(len(cards) == 0):
        initializeCards()
        cards = get_cards()
    
    return [CardBasicInfo(id=c[0], name=c[1], type=c[2]) for c in cards]


@cards_router.get("/{id}", response_model= List[CardBasicInfo])
def get_each_player_cards(id: UUID):
    cards_by_player= get_cards_by_player_id(id)
    player_cards_info= []
    for card_id in cards_by_player:
        card_info= get_card_info_by_id(card_id)
        if(not card_info):
            raise MysteryException(message="Card without info!", status_code=400)
        player_cards_info.append(card_info)
    return [CardBasicInfo(id=c[0], name=c[1], type=c[2]) for c in cards_by_player]

