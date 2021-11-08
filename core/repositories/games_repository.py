import random

from pony.orm import db_session, select, ObjectNotFound
from core import logger
from core.exceptions import MysteryException
from core.models.card_model import Mistery
from core.models.games_model import Game
from core.repositories.player_repository import find_player_by_id
from core.models.players_model import Player
from core.schemas import PlayerOutput, GameOutput
from core.schemas.player_schema import Position


@db_session
def get_games():
    return select((g.name, len(g.players), g.started) for g in Game if not g.started)[:]


@db_session
def get_game_by_name(name):
    return select(g for g in Game if g.name == name)[:]


@db_session
def new_game(game):
    g = Game(name=game.game_name)
    return Player(nickname=game.nickname, game=g, host=True)


@db_session
def find_game_by_id(uuid):
    return Game[uuid]


@db_session
def find_game_by_name(name):
    return Game.get(name=name)


@db_session
def join_player_to_game(game_join):
    g: Game = find_game_by_name(game_join.game_name)

    if g is None:
        raise MysteryException(message="Game Not found!", status_code=404)

    if g.started:
        raise MysteryException(message="Game has already been started", status_code=400)

    if len(g.players) == 6:
        raise MysteryException(message="Full game!", status_code=400)

    p = Player(nickname=game_join.nickname, game=g, host=False)

    return PlayerOutput.from_orm(p)


@db_session
def start_game_and_set_player_order(game_id):
    game = find_game_by_id(game_id)
    game.started = True

    player_count = len(game.players)
    random_list = random.sample(range(1, player_count + 1), player_count)

    for player in game.players:
        player.order = random_list.pop(0)

    game_output = GameOutput.from_orm(game)
    game_output.player_count = player_count
    cards_assignment(game_id)
    return game_output


@db_session
def cards_assignment(game_id):
    cards_id_list = list(range(21))
    random_mistery_monster = random.randint(0, 5)
    random_mistery_victim = random.randint(6, 11)
    random_mistery_enclosure = random.randint(12, 19)
    Mistery(game_id=game_id, mistery_monster=random_mistery_monster, mistery_victim=random_mistery_victim,
            mistery_enclosure=random_mistery_enclosure)
    cards_id_list.remove(random_mistery_monster)
    cards_id_list.remove(random_mistery_victim)
    cards_id_list.remove(random_mistery_enclosure)

    g = Game[game_id]
    cards_by_player = int(18 / len(g.players))
    for i in g.players:
        for j in range(cards_by_player):
            random_card = random.choice(cards_id_list)
            if (random_card == 20):
                i.witch = True
            else:
                i.cards.append(random_card)
            cards_id_list.remove(random_card)


@db_session
def find_complete_game(id):
    game_output = GameOutput.from_orm(find_game_by_id(id))
    game_output.player_count = len(game_output.players)
    return game_output


def start_game(game):
    logger.info(game)
    g: GameOutput
    p: Player
    try:
        g = find_complete_game(game.game_id)
    except ObjectNotFound:
        logger.error("Game not found [{}]".format(game.game_id))
        raise MysteryException(message="Game not found!", status_code=404)

    try:
        p = find_player_by_id(game.player_id)
    except ObjectNotFound:
        logger.error("Player not found [{}]".format(game.player_id))
        raise MysteryException(message="Player not found!", status_code=404)

    if not list(filter(lambda player: player.id == p.id and player.host, g.players)):
        raise MysteryException(message="Player not authorized!", status_code=403)

    if g.started:
        raise MysteryException(message="Game already started!", status_code=400)

    if g.player_count < 2:
        raise MysteryException(message="Game needs more join players!", status_code=400)

    return start_game_and_set_player_order(game.game_id)


@db_session
def pass_turn(game_id):
    game = find_game_by_id(game_id)
    t = 1
    if (not game.started):
        raise MysteryException(message="Game isnt started yet!", status_code=400)

    if (game.turn != len(game.players)):
        t = game.turn + 1
    game.turn = Position(t).value
    return GameOutput.from_orm(game)

@db_session
def find_enclosure_by_player_id(player_id):
    p= find_player_by_id(player_id)
    player_current_box= p.current_position
    if player_current_box.enclosure: 
        p.in_enclosure= True
    return player_current_box.enclosure

