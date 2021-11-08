from fastapi import APIRouter
from pony.orm.core import ObjectNotFound, get

from core.schemas import Movement
from core.services import move_player_service
from core.settings import logger
from core.exceptions import MysteryException
from core.schemas import Movement, Acusse
from core.repositories.games_repository import find_game_by_id
from core.repositories.card_repository import get_cards, get_card_info_by_id
from v1.endpoints.websocket_endpoints import get_wbGames

shifts_router = APIRouter()


@shifts_router.put("/move")
def move_player(movement: Movement):
    return move_player_service(movement)
    pass

@shifts_router.post("/accuse")
def accuse(accuse: Acusse):
    try:
        game = find_game_by_id(accuse.game_id)
    except ObjectNotFound:
        logger.error("Game not found [{}]".format(id))
        raise MysteryException(message="Game not found!", status_code=404)

    envelope = game.Envelop
    logger.info(envelope)
    ac = []
    ac.append(get_card_info_by_id(accuse.monster_id))
    ac.append(get_card_info_by_id(accuse.victim_id))
    ac.append(get_card_info_by_id(accuse.enclosure_id))
    if ac[0].type != "MONSTER":
        raise MysteryException(message="La carta no es un monstruo!", status_code=400)
    if ac[1].type != "VICTIM":
        raise MysteryException(message="La carta no es una victima!", status_code=400)
    if ac[2].type != "ENCLOSURE":
        raise MysteryException(message="La carta no es un recinto!", status_code=400)
    
    res = True
    for i in range(3):
        res = (ac[i].id == envelope[i].id) and res
    wb = get_wbGames(accuse.game_id)
    if res:
        wb.broadcast_message(accuse.player_id,"Gane")
    else:
        wb.broadcast_message(accuse.player_id,"Perdi")
    return res
