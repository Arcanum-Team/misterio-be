from typing import List
from fastapi import APIRouter
from uuid import UUID
from core.schemas.card_schema import CardBasicInfo
from core.exceptions import MysteryException
from core.repositories import get_card_info_by_id, get_cards
from core.models.scripts import initialize_cards
from core.services.cards_service import get_cards_by_player_id

cards_router = APIRouter()


@cards_router.get("/", response_model=List[CardBasicInfo])
def get_all_cards():
    cards = get_cards()
    return [CardBasicInfo(id=c[0], name=c[1], type=c[2]) for c in cards]


@cards_router.get("/{id}", response_model=List[CardBasicInfo])
def get_each_player_cards(id: UUID):
    cards_by_player = get_cards_by_player_id(id)
    return cards_by_player
