from logging import log
from core.settings import logger
from typing import List
from fastapi import APIRouter
from core.schemas.card_schema import CardBasicInfo
from core.models.card_repository import get_cards, initializeCards

cards_router = APIRouter()

@cards_router.get("/", response_model= List[CardBasicInfo])
def get_all_cards():
    cards = get_cards()
    if(len(cards) == 0):
        initializeCards()
        cards = get_cards()
    
    return [CardBasicInfo(id=c[0], name=c[1], type=c[2]) for c in cards]
