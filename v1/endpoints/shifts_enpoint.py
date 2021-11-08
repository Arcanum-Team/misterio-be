from fastapi import APIRouter
from pony.orm.core import ObjectNotFound, get

from core.schemas import Movement
from core.services import move_player_service
from core.settings import logger
from core.schemas import Movement, Acusse
from core.services.game_service import get_envelop
from core.services.shifts_service import valid_card
from v1.endpoints.websocket_endpoints import games


shifts_router = APIRouter()


@shifts_router.put("/move")
def move_player(movement: Movement):
    return move_player_service(movement)
    pass

@shifts_router.post("/accuse")
def accuse(accuse: Acusse):
    envelope = get_envelop(accuse.game_id)
    logger.info(envelope)
    a = []
    a.append(valid_card("ENCLOSURE", accuse.enclosure_id))
    a.append(valid_card("MONSTER", accuse.monster_id))
    a.append(valid_card("VICTIM", accuse.victim_id))
    r = set(envelope).intersection(a)
    res = False
    if not r:
        res = True
    wb = games[accuse.game_id]
    if res:
        wb.broadcast_message(accuse.player_id,"Gane")
    else:
        wb.broadcast_message(accuse.player_id,"Perdi")
    return res
