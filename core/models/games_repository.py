from pony.orm import db_session, select, commit, IntegrityError

from core.exceptions import MysteryException
from core.models.games_model import Game
from core.models.player_repository import get_player_by_id
from core.models.players_model import Player
from core.schemas import PlayerOutput
from core.schemas.games_schema import GameBasicInfo


@db_session
def get_games():
    return select((g.name, len(g.players), g.started) for g in Game if not g.started)[:]


@db_session
def get_game_by_name(name):
    return select(g for g in Game if g.name == name)[:]


@db_session
def new_game(game):
    g = Game(name=game.game_name)
    return Player(nickname=game.nickname, game=g, is_host=True)


@db_session
def find_game_by_id(uuid):
    return Game[uuid]


@db_session
def join_player_to_game(game_join):
    g: Game = find_game_by_id(game_join.game_id)

    if g.started:
        raise MysteryException(message="Game has already been started", status_code=400)

    if len(g.players) == 6:
        raise MysteryException(message="Full game!", status_code=400)

    p = Player(nickname=game_join.nickname, game=g, is_host=False)

    return PlayerOutput.from_orm(p)


@db_session
def start_game(name, host_id):
    game = get_game_by_name(name)[0]
    game.started = True
    player = get_player_by_id(host_id)
    player[0].game = game
