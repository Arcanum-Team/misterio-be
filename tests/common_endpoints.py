from fastapi.testclient import TestClient

from main import app

game_client = TestClient(app)


def get_all_games():
    return game_client.get("/api/v1/games/",
                           headers={'accept': 'application/json'})


def find_game_by_id_endpoint(id):
    return game_client.get(f"/api/v1/games/{id}",
                           headers={'accept': 'application/json'})


def get_all_cards_endpoint():
    return game_client.get("/api/v1/cards/",
                           headers={'accept': 'application/json'})


def get_board_endpoint():
    return game_client.get("api/v1/board/",
                           headers={'accept': 'application/json'})


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


def create_started_game_and_get_player_turn(nickname_host, join_players):
    new_game_response = create_game_with_n_players(join_players, nickname_host)
    game_response = start_game(new_game_response["game"]["id"], new_game_response["player"]["id"]).json()
    player_turn = next(filter(lambda p: p["order"] == 1, game_response["players"]), None)  # Get Player on turn
    assert player_turn

    return game_response, player_turn


def create_game_with_n_players(join_players, nickname_host):
    new_game_response = new_game(nickname_host).json()
    for nickname in join_players:
        join_game(new_game_response["game"]["name"], nickname).json()
    return new_game_response


def roll_dice_and_get_possible_movements(game_id, player_id, dice_value):
    possible_movements_response = roll_dice(game_id, player_id, dice_value)
    assert possible_movements_response
    assert possible_movements_response.status_code == 200
    return possible_movements_response
