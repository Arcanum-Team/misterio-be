# Game querys
from pony.orm import db_session, select, commit

from core.models.games_model import Game
from core.models.player_repository import get_player_by_id
from core.models.players_model import Player


@db_session
def get_games():
    return select(g for g in Game)[:]


@db_session
def get_game_by_name(name):
    return select(g for g in Game if g.name == name)[:]


@db_session
def add_game(name):
    g = Game(name=name)
    commit()
    return g


@db_session
def add_player(name, nickname, game_name, is_host=False):
    game = get_game_by_name(game_name)[0]
    p = Player(name=name, nikcname=nickname, gameID=game.id, isHost=is_host)
    commit()
    return p.id


@db_session
def start_game(name, host_id):
    game = get_game_by_name(name)[0]
    game.started = True
    player = get_player_by_id(host_id)
    player[0].game_id = game.id
