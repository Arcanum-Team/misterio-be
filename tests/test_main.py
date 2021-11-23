import random

from fastapi.testclient import TestClient

from main import app
from core.repositories.games_repository import find_game_by_name
from core.repositories.player_repository import find_player_by_id
from pony.orm import db_session

game_client = TestClient(app)


def new_game(nickname):
    return game_client.post("/api/v1/games/",
                            headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                            json={
                                "nickname": nickname
                            })


def join_game(game_name, nickname):
    return game_client.put("/api/v1/games/join",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_name": game_name,
                                 "nickname": nickname
                                 })


def start_game(game_id, player_id):
    return game_client.put("/api/v1/games/start",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id})


def get_cards_by_player_id(player_id):
    return game_client.get(f"/api/v1/cards/{player_id}",
                           headers={'accept': 'application/json'})


def roll_dice(game_id, player_id, dice_value):
    return game_client.put("/api/v1/shifts/roll-dice",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id, "dice": dice_value})


def move_player(game_id, player_id, box_id, dice_value):
    return game_client.put("/api/v1/shifts/move",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id, "next_box_id": box_id,
                                 "dice_value": dice_value})


def test_get_all_games():
    response = game_client.get("/api/v1/games/",
                               headers={'accept': 'application/json'})
    assert response.status_code == 200


def test_new_game():
    global game_info
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
    response = game_client.get("/api/v1/games/" + id,
                               headers={'accept': 'application/json'})
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


def test_get_all_cards():
    response = game_client.get("/api/v1/cards/",
                               headers={'accept': 'application/json'})
    assert response
    assert response.status_code == 200
    json_response = response.json()
    assert json_response
    assert len(json_response) == 20


def test_get_player_cards():
    host_player = "player1"
    new_game_response = new_game(host_player).json()

    player_2 = "player2"
    join_player_response = join_game(new_game_response["game"]["name"], player_2).json()

    start_game(new_game_response['game']['id'], new_game_response['player']['id'])

    cards_host_player_response = get_cards_by_player_id(new_game_response['player']['id'])

    assert cards_host_player_response
    assert cards_host_player_response.status_code == 200

    cards_host_player_json = cards_host_player_response.json()
    assert len(cards_host_player_json) > 1

    join_player_response = get_cards_by_player_id(join_player_response['player']['id'])

    assert join_player_response
    assert join_player_response.status_code == 200

    cards_join_player_json = join_player_response.json()
    assert len(cards_join_player_json) > 1

    assert set(
        map(lambda c: c["id"], cards_host_player_json)
    ).intersection(
        map(lambda c: c["id"], cards_join_player_json)
    ) == set()


def test_get_board():
    response = game_client.get("api/v1/board/",
                               headers={'accept': 'application/json'})
    assert response.status_code == 200
    json_response = response.json()
    for row in json_response:
        assert row
        assert row["id"]
        assert row["boxes"]
        assert len(row["boxes"]) == 20


def test_move_player():
    new_game_response = new_game("player1").json()

    join_game(new_game_response["game"]["name"], "player2").json()

    game_response = start_game(new_game_response["game"]["id"], new_game_response["player"]["id"]).json()

    player_turn = next(filter(lambda p: p["order"] == 1, game_response["players"]), None)  # Get Player on turn

    assert player_turn

    dice_value = 6
    possible_movements_response = roll_dice(game_response["game"]["id"], player_turn["id"], dice_value)
    assert possible_movements_response
    assert possible_movements_response.status_code == 200
    possible_movements_json = possible_movements_response.json()

    new_position_box = random.choice(possible_movements_json)

    player_new_position_response = move_player(game_response["game"]["id"], player_turn["id"],
                                               new_position_box, dice_value)

    # EP validation
    assert player_new_position_response
    assert player_new_position_response.status_code == 200
    player_new_position_json = player_new_position_response.json()

    assert player_new_position_json["player"]["current_position"]["id"] == new_position_box

    # DB validation
    with db_session:
        player = find_player_by_id(player_turn["id"])
        assert player.current_position.id == new_position_box
