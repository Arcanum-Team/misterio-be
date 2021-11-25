from pony.orm import db_session

from core.repositories import find_player_by_id
from core.repositories.games_repository import find_game_by_name
from tests.util_functions import get_all_games, new_game, join_game, find_game_by_id_endpoint, new_game_by_name, \
    string_generator, new_game_by_password, create_game_with_n_players, create_started_game


def test_get_all_games_ok():
    new_game_json = new_game("player1").json()
    response = get_all_games()
    assert response.status_code == 200
    all_games_json = response.json()
    assert len(all_games_json) > 0
    assert next(filter(lambda g: g["name"] == new_game_json["game"]["name"], all_games_json), None)


def test_new_game_ok():
    response = new_game("player1")
    game_info = response.json()
    assert response.status_code == 201
    with db_session:
        player = find_player_by_id(game_info["player"]["id"])
        assert player
        assert player.game
        assert player.game.name
        assert not player.game.started


def test_new_game_with_name_ok():
    game_name = string_generator(6)
    response = new_game_by_name("player1", game_name)
    game_info = response.json()
    assert response.status_code == 201
    with db_session:
        player = find_player_by_id(game_info["player"]["id"])
        assert player
        assert player.game.name == game_name


def test_new_game_with_invalid_name_fail():
    game_name = string_generator(7)
    response = new_game_by_name("player1", game_name)
    assert response.status_code == 422


def test_new_game_with_duplicated_name_fail():
    game_name = string_generator(6)
    new_game_by_name("player1", game_name)
    response = new_game_by_name("player1", game_name)
    assert response.status_code == 400


def test_new_game_with_password_ok():
    password = string_generator(10)
    response = new_game_by_password("player1", password)
    game_info = response.json()
    assert response.status_code == 201
    with db_session:
        player = find_player_by_id(game_info["player"]["id"])
        assert player
        assert player.game.password == password


def test_new_game_with_invalid_password_fail():
    password = string_generator(11)
    response = new_game_by_password("player1", password)
    assert response.status_code == 422


def test_join_player_in_game_ok():
    new_game_response = new_game("player1").json()

    response = join_game(new_game_response["game"]["name"], "player2")
    join_body = response.json()
    assert response.status_code == 200
    with db_session:
        game = find_game_by_name(join_body["game"]["name"])
        player = find_player_by_id(join_body["player"]["id"])
        assert len(game.players) == join_body["game"]["player_count"]
        assert player


def test_join_player_with_full_game_fail():
    new_game_response = create_game_with_n_players("one", ["two", "three", "four", "five", "six"])

    response = join_game(new_game_response["game"]["name"], "seven")
    assert response.status_code == 400


def test_get_game_by_id():
    new_game_response = new_game("player1").json()
    id = new_game_response['game']['id']
    response = find_game_by_id_endpoint(id)
    assert response.status_code == 200
    assert response.json()
    assert response.json()["game"]
    assert response.json()["game"]["id"]
    assert response.json()["game"]["id"] == id


def test_start_game_ok():
    started_game, player_host = create_started_game("one", ["two", "three", "four", "five", "six"])
    assert started_game.status_code == 200
    response_json = started_game.json()
    assert response_json["game"]
    assert response_json["game"]["id"]
    assert response_json["players"]
    assert len(response_json["players"]) == 6

    with db_session:
        player = find_player_by_id(player_host["id"])
        assert player
        assert player.game
        assert player.game.started
        assert player.game.turn == 1
        assert len(response_json["players"]) == len(player.game.players)
        assert next(filter(lambda p: p.nickname == player_host["nickname"], player.game.players), None)
        assert next(filter(lambda p: p.witch, player.game.players), None)  # One player have witch card
        for player in player.game.players:
            assert player.order
            assert player.color


def test_start_game_with_one_player_fail():
    started_game, player_host = create_started_game("one", [])
    assert started_game.status_code == 400

