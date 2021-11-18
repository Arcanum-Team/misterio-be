from uuid import UUID

from pony.orm import ObjectNotFound

from core import logger
from core.exceptions import MysteryException
from core.repositories import find_complete_game, start_game, find_game_by_id, join_player_to_game, is_valid_game_player
from core.schemas import GameStart, GameJoin


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


def start_new_game(game: GameStart):
    return start_game(game)
    # hide_player_id(game_started)


def hide_player_id(game):
    # Hide ids
    for player in game.players:
        player.id = None


def get_envelop(game_id):
    game = find_game_by_id(game_id)
    return game.envelop


def join_player(game_join: GameJoin):
    return join_player_to_game(game_join)


def is_valid_game_player_service(game_id, player_id):
    try:
        is_valid_game_player(game_id, player_id)
    except ObjectNotFound:
        raise MysteryException(message="Game not found!", status_code=404)

