from pony.orm import db_session, select, commit, IntegrityError

from core.models.games_model import Game
from core.models.player_repository import get_player_by_id
from core.models.players_model import Player
from core.schemas import PlayerOutput


@db_session
def get_games():
    return select(g for g in Game)[:]


@db_session
def get_game_by_name(name):
    return select(g for g in Game if g.name == name)[:]


@db_session
def new_game(game):
        g = Game(name=game.game_name)
        p = Player(nickname=game.nickname, game=g, is_host=True)
        return PlayerOutput.from_orm(p)


@db_session
def get_by_id(uuid):
    return Game[uuid]


@db_session
def add_player(name, nickname, game_name, is_host=False):
    game = get_game_by_name(game_name)[0]
    p = Player(nikcname=nickname, game=game, isHost=is_host)
    commit()
    return p.id


@db_session
def start_game(name, host_id):
    game = get_game_by_name(name)[0]
    game.started = True
    player = get_player_by_id(host_id)
    player[0].game = game
