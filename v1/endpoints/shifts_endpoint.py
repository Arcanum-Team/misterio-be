from fastapi import APIRouter

from core.schemas.games_schema import BasicGameInput
from core.settings import logger, get_live_game_room
from core.services import set_loser_service, get_possible_movement, suspect_service, \
    roll_dice_service, enclosure_enter_service, enclosure_exit_service, suspect_response_service, valid_cards, \
    find_player_pos_service, move_player_service, get_envelop, valid_is_started
from core.schemas import Movement, Acusse, RollDice, Message, DataAccuse, PlayerBox, GamePlayer, \
    DataRoll, SuspectResponse


shifts_router = APIRouter()


@shifts_router.put("/move")
async def move_player(movement: Movement):
    return await move_player_service(movement)


@shifts_router.post("/accuse")
def accuse(accuse_input: Acusse):
    valid_cards(accuse_input)
    valid_is_started(accuse_input.game_id)
    envelope = get_envelop(accuse_input.game_id)
    logger.info(envelope)
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


@shifts_router.post("/suspect")
async def suspect(suspect_input: Acusse):
    await suspect_service(suspect_input)


@shifts_router.post("/suspectResponse")
async def suspect_response(response: SuspectResponse):
    return await suspect_response_service(response)


@shifts_router.put("/roll-dice")
async def roll_dice(roll: RollDice):
    return await roll_dice_service(roll)


@shifts_router.put("/enclosure/enter", response_model=GamePlayer)
async def enclosure_enter(player_game: BasicGameInput):
    return await enclosure_enter_service(player_game)


@shifts_router.put("/enclosure/exit", response_model=GamePlayer)
async def enclosure_exit(player_game: PlayerBox):
    return await enclosure_exit_service(player_game)
