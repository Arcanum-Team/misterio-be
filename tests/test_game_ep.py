from pony.orm import db_session

from core.repositories import find_player_by_id
from core.repositories.games_repository import find_game_by_name
from tests.common_endpoints import get_all_games, new_game, join_game, find_game_by_id_endpoint, start_game


def test_get_all_games():
    response = get_all_games()
    assert response.status_code == 200


def test_new_game():
    response = new_game("player1")
    game_info = response.json()
    with db_session:
        game = find_game_by_name(game_info["game"]["name"])
        player = find_player_by_id(game_info["player"]["id"])
        assert game
        assert player
    assert response.status_code == 201


def test_join_game():
    new_game_response = new_game("player1").json()

    response = join_game(new_game_response["game"]["name"], "player2")
    join_body = response.json()
    assert response.status_code == 200
    with db_session:
        game = find_game_by_name(join_body["game"]["name"])
        player = find_player_by_id(join_body["player"]["id"])
        assert len(game.players) == join_body["game"]["player_count"]
        assert player


def test_get_game_by_id():
    new_game_response = new_game("player1").json()
    id = new_game_response['game']['id']
    response = find_game_by_id_endpoint(id)
    assert response.status_code == 200
    assert response.json()
    assert response.json()["game"]
    assert response.json()["game"]["id"]
    assert response.json()["game"]["id"] == id


def test_start_game():
    nickname_host = "player1"
    new_game_response = new_game(nickname_host).json()

    nickname_joined_player = "player2"
    join_game(new_game_response["game"]["name"], nickname_joined_player).json()

    response = start_game(new_game_response["game"]["id"], new_game_response["player"]["id"])

    assert response.status_code == 200
    response_json = response.json()
    assert response_json["game"]
    assert response_json["game"]["id"]
    assert response_json["game"]["id"] == new_game_response["game"]["id"]
    assert response_json["players"]
    assert len(response_json["players"]) > 1

    with db_session:
        game = find_game_by_name(new_game_response['game']["name"])
        assert game.started
        assert game.turn == 1
        for player in game.players:
            assert player.order
            assert player.color
        assert len(response_json["players"]) == len(game.players)
        assert next(filter(lambda p: p.nickname == nickname_host, game.players), None)
        assert next(filter(lambda p: p.nickname == nickname_joined_player, game.players), None)
        assert next(filter(lambda p: p.witch, game.players), None)  # One player have witch card
