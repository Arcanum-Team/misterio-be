import json
from uuid import UUID

from pony.orm import ObjectNotFound

from core import logger, LiveGameRoom, get_live_game_room
from core.exceptions import MysteryException
from core.repositories import find_complete_game, find_game_by_id, join_player_to_game, is_valid_game_player, \
    start_game_and_set_player_order
from core.schemas import GameJoin, GameListPlayers
from core.schemas.player_schema import BasicGameInput


def get_valid_game(player_id: UUID, game_id: UUID):
    game = find_game_by_id_service(game_id)

    if player_id not in map(lambda player: player.id, game.players):
        logger.error(f"The player [{player_id}] does not belong to the game [{game_id}]")
        raise MysteryException(message="Invalid Player!", status_code=400)

    return game


def find_game_by_id_service(game_id):
    try:
        return find_complete_game(game_id)
    except ObjectNotFound:
        logger.error("Game not found [{}]".format(game_id))
        raise MysteryException(message="Game not found!", status_code=404)


def find_game_hide_player_id(game_id):
    game = find_game_by_id_service(game_id)
    # hide_player_id(game)
    return game


async def start_new_game(game: BasicGameInput):
    logger.info(game)
    try:
        game_players: GameListPlayers = start_game_and_set_player_order(game.game_id, game.player_id)
        room: LiveGameRoom = get_live_game_room(game.game_id)
        #await room.broadcast_json_message("START_GAME", json.loads(game_players.json()))
        return game_players
    except ObjectNotFound:
        logger.error("Game not found [{}]".format(game.game_id))
        raise MysteryException(message="Game not found!", status_code=404)


def hide_player_id(game):
    # Hide ids
    for player in game.players:
        player.id = None


def get_envelop(game_id):
    game = find_game_by_id(game_id)
    return game.envelop


def valid_is_started(game_id):
    game = find_game_by_id(game_id)
    if not game.started:
        raise MysteryException(message="Game is not started", status_code=400)


def join_player(game_join: GameJoin):
    return join_player_to_game(game_join)


def is_valid_game_player_service(game_id, player_id):
    try:
        is_valid_game_player(game_id, player_id)
    except ObjectNotFound:
        raise MysteryException(message="Game not found!", status_code=404)
