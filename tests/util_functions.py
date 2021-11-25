import random
import string

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


def new_game_by_name(nickname, game_name):
    return game_client.post("/api/v1/games/",
                            headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                            json={
                                "nickname": nickname,
                                "game_name": game_name
                            })


def new_game_by_password(nickname, password):
    return game_client.post("/api/v1/games/",
                            headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                            json={
                                "nickname": nickname,
                                "optional_password": password
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


def enclosure_enter(game_id, player_id):
    return game_client.put("/api/v1/shifts/enclosure/enter",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id})


def enclosure_exit(game_id, player_id, exit_door):
    return game_client.put("/api/v1/shifts/enclosure/exit",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id, "box_id": exit_door})


def accuse(game_id, player_id, enclosure_id, monster_id, victim_id):
    return game_client.put("/api/v1/shifts/accuse",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id, "enclosure_id": enclosure_id,
                                 "monster_id": monster_id, "victim_id": victim_id})


def suspect(game_id, player_id, monster_id, victim_id):
    return game_client.put("/api/v1/shifts/suspect",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id,"monster_id": monster_id,
                                "victim_id": victim_id})


def suspect_response_card(game_id, from_player, to_player, card):
    return game_client.put("/api/v1/shifts/response_suspect_card",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "from_player": from_player,"to_player": to_player,
                                "card": card})


def pass_turn(game_id, player_id):
    return game_client.put("/api/v1/shifts/pass",
                        headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                        json={"game_id": game_id, "player_id": player_id})


def create_started_game_and_get_player_turn(nickname_host, join_players):
    game_response = create_started_game(nickname_host, join_players)[0].json()
    player_turn = next(filter(lambda p: p["order"] == 1, game_response["players"]), None)  # Get Player on turn
    assert player_turn

    return game_response, player_turn


def create_started_game(nickname_host, join_players):
    new_game_response = create_game_with_n_players(nickname_host, join_players)
    player_host = next(filter(lambda p: p["nickname"] == nickname_host, new_game_response["players"]), None)
    started_game = start_game(new_game_response["game"]["id"], player_host["id"])
    return started_game, player_host


def create_game_with_n_players(nickname_host, join_players):
    new_game_response = new_game(nickname_host).json()
    for nickname in join_players:
        join_game(new_game_response["game"]["name"], nickname)
    return find_game_by_id_endpoint(new_game_response["game"]["id"]).json()


def roll_dice_and_get_possible_movements(game_id, player_id, dice_value):
    possible_movements_response = roll_dice(game_id, player_id, dice_value)
    assert possible_movements_response
    assert possible_movements_response.status_code == 200
    return possible_movements_response


def string_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_enclosure_box_id(possible_movements):
    board = get_board_endpoint().json()
    all_boxes = list()
    for r in board:
        all_boxes.extend(r["boxes"])
    enclosures_enter = list(filter(lambda b: b["attribute"] in ["ENCLOSURE_DOWN", "ENCLOSURE_UP"], all_boxes))
    return set(map(lambda b: b["id"], enclosures_enter)).intersection(set(possible_movements)).pop()


def get_enclosure_by_game_id_and_player_id(game_id, player_id, dice):
    possible_movements = roll_dice_and_get_possible_movements(game_id, player_id, dice).json()
    enclosure_box_id = get_enclosure_box_id(possible_movements)
    return enclosure_box_id

def put_execute_witch(game_id, player_id):
    return game_client.put("/api/v1/shifts/execute_witch",
                           headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                           json={"game_id": game_id, "player_id": player_id})