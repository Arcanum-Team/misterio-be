from fastapi import APIRouter
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from core.schemas.games_schema import BasicGameInput
from core.services import suspect_service, roll_dice_service, enclosure_enter_service, \
    enclosure_exit_service, suspect_response_service, move_player_service, pass_turn_service, accuse_service
from core.schemas import Movement, Acusse, RollDice, PlayerBox, GamePlayer, SuspectResponse, Suspect


shifts_router = APIRouter()


@shifts_router.put("/move")
async def move_player(movement: Movement):
    return await move_player_service(movement)


@shifts_router.put("/accuse")
async def accuse(accuse_input: Acusse):
    return await accuse_service(accuse_input)


@shifts_router.put("/suspect")
async def suspect(suspect_input: Suspect):
    await suspect_service(suspect_input)


@shifts_router.put("/send_suspect_card")
async def send_suspect_card(response: SuspectResponse):
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


@shifts_router.put("/pass", status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def pass_game_turn(player_game: BasicGameInput):
    await pass_turn_service(player_game)
