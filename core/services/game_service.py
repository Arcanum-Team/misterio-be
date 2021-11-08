from uuid import UUID

from pony.orm import ObjectNotFound

from core import logger
from core.exceptions import MysteryException
from core.repositories import find_complete_game
from core.schemas import GameOutput


def get_valid_game(player_id: UUID, game_id: UUID):
    game: GameOutput
    try:
        game = find_complete_game(game_id)
    except ObjectNotFound:
        logger.error("Game not found [{}]".format(game_id))
        raise MysteryException(message="Game not found!", status_code=404)

    if player_id not in map(lambda player: player.id ,game.players):
        logger.error(f"The player [{player_id}] does not belong to the game [{game_id}]")
        raise MysteryException(message="Invalid Player!", status_code=400)

    return game
