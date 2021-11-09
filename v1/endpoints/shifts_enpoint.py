from fastapi import APIRouter
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
def accuse(accuse_input: Acusse):
    envelope = get_envelop(accuse_input.game_id)
    logger.info(envelope)
    valid_card("ENCLOSURE", accuse_input.enclosure_id)
    valid_card("MONSTER", accuse_input.monster_id)
    valid_card("VICTIM", accuse_input.victim_id)
    a = {accuse_input.enclosure_id, accuse_input.monster_id, accuse_input.victim_id}

    r = set(envelope).difference(a)
    res = False
    if len(r) == 0:
        res = True
    """
    wb = games[accuse_input.game_id]
    if res:
        wb.broadcast_message(accuse_input.player_id, "Gane")
    else:
        wb.broadcast_message(accuse_input.player_id, "Perdi")
    """
    return res
