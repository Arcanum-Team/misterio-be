import random
from typing import Set, List, Dict

from pony.orm import db_session, select
from core import logger
from core.models import Card, Box, Player, Game
from core.repositories import get_boxes_by_type, get_card_by_id, get_cards
from core.exceptions import MysteryException
from core.schemas import PlayerOutput, GameOutput, GameListPlayers, GamePlayer, Suspect, DataSuspectNotice, Acusse, \
    DataAccuse
from core.repositories.player_repository import player_to_player_output, find_player_by_id, find_next_available_player, \
    find_available_players_without_me, get_next_turn


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
    return GamePlayer(game=game_to_game_output(g),
                      player=player_to_player_output(player))


@db_session
def game_to_game_output(g):
    game_output = GameOutput.from_orm(g)
    game_output.player_count = len(g.players)
    return game_output


@db_session
def find_game_by_id(uuid):
    return Game[uuid]


@db_session
def get_game_players_count(uuid):
    return len(Game[uuid].players)


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

    return GamePlayer(game=game_to_game_output(g),
                      player=player_to_player_output(p))


@db_session
def start_game_and_set_player_order(game_id, player_id):
    player: Player = find_valid_player(game_id, player_id)

    game: Game = player.game

    if not player.host:
        raise MysteryException(message="Player not authorized!", status_code=403)

    if game.started:
        raise MysteryException(message="Game already started!", status_code=400)

    if len(game.players) < 2:
        raise MysteryException(message="Game needs more join players!", status_code=400)

    # START SET INITIAL GAME
    game.started = True
    game.turn = 1

    cards: Set[Card] = get_cards()
    cards_id_list: List[int] = list(map(lambda x: x.id, cards))
    enclosures_id_list = list(map(lambda x: x.id, filter(lambda card: card.type == "ENCLOSURE", cards)))
    victims_id_list = list(map(lambda x: x.id, filter(lambda card: card.type == "VICTIM", cards)))
    monsters_id_list = list(map(lambda x: x.id, filter(lambda card: card.type == "MONSTER", cards)))

    colors = ["blue", "green", "orange", "red", "white", "yellow"]

    random_mystery_enclosure = random.choice(enclosures_id_list)
    random_mystery_monster = random.choice(monsters_id_list)
    random_mystery_victim = random.choice(victims_id_list)
    envelop = [random_mystery_enclosure, random_mystery_monster, random_mystery_victim]
    cards_id_list.remove(random_mystery_monster)
    cards_id_list.remove(random_mystery_victim)
    cards_id_list.remove(random_mystery_enclosure)
    cards_id_list.append(21)  # ADD WITCH CARD
    game.envelop = envelop

    players: Dict[int, List[Card]] = {}

    entries: List[Box] = list(get_boxes_by_type("ENTRY"))

    # Initialize players dict and set
    for player in game.players:
        box = random.choice(entries)
        color = random.choice(colors)
        player.current_position = box
        player.color = color
        colors.remove(color)
        entries.remove(box)
        players[player.id] = list()

    player_with_witch = None
    # Distribute rest of cards
    while len(cards_id_list) > 0:
        for key, value in players.items():
            card_id = random.choice(cards_id_list)
            if card_id == 21:
                player_with_witch = key
            else:
                value.append(get_card_by_id(card_id))
            cards_id_list.remove(card_id)
            if len(cards_id_list) == 0:
                break

    for key, value in players.items():
        player: Player = next(filter(lambda p: p.id == key, game.players))
        player.cards = value
        if key == player_with_witch:
            player.witch = True

    player_count = len(game.players)
    random_list = random.sample(range(1, player_count + 1), player_count)

    for player in game.players:
        player.order = random_list.pop(0)

    # END SET INITIAL GAME

    game_output = GameOutput.from_orm(game)
    game_output.player_count = player_count

    players_list: List[PlayerOutput] = [player_to_player_output(player) for player in game.players]
    players_list.sort(key=lambda p: p.order)

    return GameListPlayers(game=game_output, players=players_list)


@db_session
def find_complete_game(id):
    game: Game = find_game_by_id(id)
    game_field: GameOutput = GameOutput.from_orm(game)
    game_field.player_count = len(game.players)
    players_list: List[PlayerOutput] = [player_to_player_output(player) for player in game.players]
    if game.started:
        players_list.sort(key=lambda player: player.order)

    return GameListPlayers(game=game_field, players=players_list)


@db_session
def pass_shift(game_id, player_id):
    player: Player = find_player_game_started_in_turn(game_id, player_id)
    next_player: Player = find_next_available_player(player)
    next_player.game.turn = next_player.order
    return GamePlayer(game=GameOutput.from_orm(next_player.game), player=player_to_player_output(next_player))


@db_session
def find_player_by_id_and_game_id(player_id, game_id):
    player = find_valid_player(game_id, player_id)
    return GamePlayer(game=GameOutput.from_orm(player.game), player=player_to_player_output(player))


@db_session
def find_valid_player(game_id, player_id):
    logger.info(f"Find Player [game: {game_id} player: {player_id}]")
    game: Game = find_game_by_id(game_id)
    player: Player = next(filter(lambda p: p.id == player_id, game.players), None)
    if not player:
        raise MysteryException(message="Player Not found!", status_code=404)
    return player


@db_session
def find_player_game_started_in_turn(game_id, player_id):
    player: Player = find_valid_player(game_id, player_id)

    if not player.game.started:
        raise MysteryException(message="Game Not started!", status_code=400)

    if player.order != player.game.turn:
        raise MysteryException(message="Player Not turn!", status_code=400)

    return player


@db_session
def get_player_reached(player, suspect_cards):
    players_len = len(player.game.players)
    player_turn = player.order
    next_turn = get_next_turn(player_turn, players_len)
    while player_turn != next_turn:
        player_found: Player = find_player_by_turn(player.game.players, next_turn)
        if len(set(map(lambda c: c.id, player_found.cards)).intersection(suspect_cards)) > 0:
            return player_found.id
        next_turn = get_next_turn(next_turn, players_len)
    return None


@db_session
def do_suspect(suspect: Suspect):
    player: Player = find_player_game_started_in_turn(suspect.game_id, suspect.player_id)
    if not player.enclosure:
        raise MysteryException(message="Player is not in enclosure!", status_code=400)
    enclosure_id = player.enclosure.id
    player_reached = get_player_reached(player, {enclosure_id, suspect.monster_id, suspect.victim_id})
    return DataSuspectNotice(player_id=suspect.player_id, reached_player_id=player_reached,
                             enclosure_id=enclosure_id, monster_id=suspect.monster_id,
                             victim_id=suspect.victim_id, game_id=suspect.game_id)


@db_session
def do_accuse(accuse: Acusse):
    player: Player = find_player_game_started_in_turn(accuse.game_id, accuse.player_id)
    envelop = player.game.envelop
    accuse_cards = {accuse.enclosure_id, accuse.monster_id, accuse.victim_id}
    if len(set(envelop).difference(accuse_cards)) == 0:
        player_output = player_to_player_output(player)
        return DataAccuse(player=player_output,
                          game=game_to_game_output(player.game),
                          player_win=player_output,
                          cards=envelop,
                          )
    else:
        next_player = player_to_player_output(find_next_available_player(player))
        player.loser = True
        player.game.turn = next_player.order
        data_accuse = DataAccuse(player=player_to_player_output(player), game=game_to_game_output(player.game),
                                 cards=accuse_cards)
        if len(find_available_players_without_me(player)) == 1:
            data_accuse.player_win = next_player
        else:
            data_accuse.next_player_turn = next_player
        return data_accuse


@db_session
def find_player_by_turn(players, turn):
    return next(filter(lambda p: p.order == turn, players), None)


@db_session
def is_valid_game_player(game_id, player_id):
    find_valid_player(game_id, player_id)
