from typing import List
from fastapi import APIRouter
from uuid import UUID
from core.schemas.card_schema import CardBasicInfo
from core.services.cards_service import get_cards_by_player_id, get_all_cards
from core.repositories.card_repository import witch

cards_router = APIRouter()


@cards_router.get("/", response_model=List[CardBasicInfo])
def get_all_cards_endpoint():
    return get_all_cards()


@cards_router.get("/{id}", response_model=List[CardBasicInfo])
def get_each_player_cards(id: UUID):
    cards_by_player = get_cards_by_player_id(id)
    return cards_by_player

@cards_router.get("/witch/{id}")
def get_one_mistery_card_by_witch(id: UUID):
    return witch(id)
