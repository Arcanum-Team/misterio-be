from fastapi import APIRouter
from core.services import move_player_service
from core.settings import logger, get_live_game_room
from core.schemas import Movement, Acusse, RollDice, Message, DataAccuse, BasicGameInput, PlayerBox, GamePlayer
from core.services.game_service import get_envelop
from core.services.shifts_service import set_loser_service, valid_card, roll_dice_service, enclosure_enter_service, \
    enclosure_exit_service

shifts_router = APIRouter()


@shifts_router.put("/move")
async def move_player(movement: Movement):
    return await move_player_service(movement)


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


@shifts_router.put("/roll-dice")
async def roll_dice(roll: RollDice):
    return await roll_dice_service(roll)


@shifts_router.put("/enclosure/enter", response_model=GamePlayer)
async def enclosure_enter(player_game: BasicGameInput):
    return await enclosure_enter_service(player_game)


@shifts_router.put("/enclosure/exit", response_model=GamePlayer)
async def enclosure_exit(player_game: PlayerBox):
    return await enclosure_exit_service(player_game)
