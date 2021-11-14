from uuid import UUID
from fastapi import APIRouter
from core.services import move_player_service, find_player_pos_service
from core.settings import logger, get_live_game_room
from core.schemas import Movement, Acusse, RollDice, Message, DataAccuse, DataRoll
from core.services.game_service import get_envelop
from core.services.shifts_service import set_loser_service, valid_card, get_possible_movement
#from v1.endpoints.websocket_endpoints import games
from core.repositories.player_repository import find_enclosure_by_player_id


shifts_router = APIRouter()


@shifts_router.put("/move")
def move_player(movement: Movement):
    return move_player_service(movement)


@shifts_router.put("/enter_enclosure/{player_id}")
def enter_enclosure(player_id: UUID):
    return find_enclosure_by_player_id(player_id)


@shifts_router.post("/accuse")
def accuse(accuse_input: Acusse):
    envelope = get_envelop(accuse_input.game_id)
    logger.info(envelope)
    valid_card("ENCLOSURE", accuse_input.enclosure_id)
    valid_card("MONSTER", accuse_input.monster_id)
    valid_card("VICTIM", accuse_input.victim_id)
    accuse = [accuse_input.enclosure_id, accuse_input.monster_id, accuse_input.victim_id]
    player_id = accuse_input.player_id
    r = set(envelope).difference(accuse)
    if len(r) == 0:
        data = DataAccuse(player_id=player_id, result=True, cards=envelope)
        message = Message(type="Accuse", data=data)
    else:
        data = DataAccuse(player_id=player_id, result=False, cards=accuse)
        message = Message(type="Accuse", data=data)
        set_loser_service(player_id)

    wb = get_live_game_room(accuse_input.game_id)
    wb.broadcast_message(message)

    return message


@shifts_router.put("/rollDice")
def roll_dice(roll: RollDice):
    pos = find_player_pos_service(RollDice.player_id)
    possible_boxes = get_possible_movement(RollDice.dice, pos)
    wb = get_live_game_room(roll.game_id)
    data = DataRoll(player_id=roll.player_id, dice=roll.dice)
    message = Message(type="RollDice", data=data)
    wb.broadcast_message(message)
    return possible_boxes

