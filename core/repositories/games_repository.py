import random
from typing import Set, List, Dict

from pony.orm import db_session, select, ObjectNotFound
from core import logger
from core.exceptions import MysteryException
from core.models import Card, Box
from core.models.games_model import Game
from core.repositories import get_boxes_by_type
from core.repositories.player_repository import find_player_by_id, player_to_player_output
from core.models.players_model import Player
from core.schemas import PlayerOutput, GameOutput, GameListPlayers, GamePlayer
from core.repositories.card_repository import get_card_by_id, get_cards


@db_session
def get_games():
    return select((g.name, len(g.players), g.started) for g in Game if not g.started)[:]


@db_session
def get_game_by_name(name):
    return Game.select(name=name)


@db_session
def new_game(game):
    g = Game(name=game.game_name)
    player = Player(nickname=game.nickname, game=g, host=True)
    return GamePlayer(game=GameOutput.from_orm(g),
                      player=PlayerOutput(id=player.id, nickname=player.nickname, host=player.host))


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

    return GamePlayer(game=GameOutput.from_orm(g),
                      player=PlayerOutput(id=p.id, nickname=p.nickname, host=p.host))


@db_session
def start_game_and_set_player_order(game_id):
    game = cards_assignment(game_id)
    game.started = True
    game.turn = 1

    player_count = len(game.players)
    random_list = random.sample(range(1, player_count + 1), player_count)
    logger.info(f"random: {random_list}")
    for player in game.players:
        player.order = random_list.pop(0)

    game_output = GameOutput.from_orm(game)
    game_output.player_count = player_count

    players_list: List[PlayerOutput] = [player_to_player_output(player) for player in game.players]
    players_list.sort(key=lambda p: p.order)

    return GameListPlayers(game=game_output, players=players_list)


@db_session
def cards_assignment(game_id):
    cards: Set[Card] = get_cards()
    cards_id_list: List[int] = list(map(lambda x: x.id, cards))
    enclosures_id_list = list(map(lambda x: x.id, filter(lambda card: card.type == "ENCLOSURE", cards)))
    victims_id_list = list(map(lambda x: x.id, filter(lambda card: card.type == "VICTIM", cards)))
    monsters_id_list = list(map(lambda x: x.id, filter(lambda card: card.type == "MONSTER", cards)))

    random_mystery_enclosure = random.choice(enclosures_id_list)
    random_mystery_monster = random.choice(monsters_id_list)
    random_mystery_victim = random.choice(victims_id_list)
    envelop = [random_mystery_enclosure, random_mystery_monster, random_mystery_victim]
    cards_id_list.remove(random_mystery_monster)
    cards_id_list.remove(random_mystery_victim)
    cards_id_list.remove(random_mystery_enclosure)

    game: Game = find_game_by_id(game_id)
    game.envelop = envelop

    players: Dict[int, List[Card]] = {}

    entries: List[Box] = list(get_boxes_by_type("ENTRY"))

    # Initialize players dict and set
    for player in game.players:
        box = random.choice(entries)
        player.current_position = box
        entries.remove(box)
        players[player.id] = list()

    # Distribute rest of cards
    while len(cards_id_list) > 0:
        for value in players.values():
            card_id = random.choice(cards_id_list)
            value.append(get_card_by_id(card_id))
            cards_id_list.remove(card_id)
            if len(cards_id_list) == 0:
                break

    for key, value in players.items():
        player: Player = next(filter(lambda p: p.id == key, game.players))
        player.cards = value

    return game


@db_session
def find_complete_game(id):
    game: Game = find_game_by_id(id)
    game_field: GameOutput = GameOutput.from_orm(game)
    game_field.player_count = len(game.players)
    players_list: List[PlayerOutput] = [player_to_player_output(player) for player in game.players]
    if game.started:
        players_list.sort(key=lambda player: player.order)

    return GameListPlayers(game=game_field, players=players_list)


def start_game(game):
    logger.info(game)
    game_list_players: GameOutput
    p: Player
    try:
        game_list_players: GameListPlayers = find_complete_game(game.game_id)
    except ObjectNotFound:
        logger.error("Game not found [{}]".format(game.game_id))
        raise MysteryException(message="Game not found!", status_code=404)

    try:
        p = find_player_by_id(game.player_id)
    except ObjectNotFound:
        logger.error("Player not found [{}]".format(game.player_id))
        raise MysteryException(message="Player not found!", status_code=404)

    if not list(filter(lambda player: player.id == p.id and player.host, game_list_players.players)):
        raise MysteryException(message="Player not authorized!", status_code=403)

    if game_list_players.game.started:
        raise MysteryException(message="Game already started!", status_code=400)

    if game_list_players.game.player_count < 2:
        raise MysteryException(message="Game needs more join players!", status_code=400)

    return start_game_and_set_player_order(game.game_id)


@db_session
def pass_turn(game_id):
    game = find_game_by_id(game_id)
    t = 1
    if not game.started:
        raise MysteryException(message="Game isnt started yet!", status_code=400)

    if game.turn < len(game.players):
        t = game.turn + 1
    game.turn = t
    return GameOutput.from_orm(game)


@db_session
def find_player_by_id_and_game_id(player_id, game_id):
    player = find_valid_player(game_id, player_id)
    return GamePlayer(game=GameOutput.from_orm(player.game), player=player_to_player_output(player))


@db_session
def find_valid_player(game_id, player_id):
    logger.info(f"Find Player [game: {game_id} player: {player_id}]")
    game: Game = find_game_by_id(game_id)
    player: Player = next(filter(lambda p: p.id == player_id, game.players))
    if not player:
        raise MysteryException(message="Player Not found!", status_code=404)
    return player


@db_session
def is_valid_game_player(game_id, player_id):
    find_valid_player(game_id, player_id)
