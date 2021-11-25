import random
from pony.orm import db_session
from core.services import get_envelop
from core.repositories import find_player_by_id
from tests.util_functions import create_game_with_n_players, move_player, create_started_game_and_get_player_turn, \
    roll_dice_and_get_possible_movements, get_enclosure_box_id, enclosure_enter, accuse, \
    get_enclosure_by_game_id_and_player_id, enclosure_exit, new_game, join_game, start_game, put_execute_witch, suspect, suspect_response_card, \
    pass_turn


def get_wrong_box(possible_movements_json):
    return list(set(range(1, 81)).difference(set(possible_movements_json)))


def test_move_player_ok():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])

    dice_value = 6
    possible_movements_response = roll_dice_and_get_possible_movements(game_response["game"]["id"], player_turn["id"],
                                                                       dice_value)
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


def test_move_player_wrong_movement():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])

    dice_value = 6
    possible_movements_response = roll_dice_and_get_possible_movements(game_response["game"]["id"], player_turn["id"],
                                                                       dice_value)
    possible_movements_json = possible_movements_response.json()

    new_position_box = random.choice(get_wrong_box(possible_movements_json))

    player_new_position_response = move_player(game_response["game"]["id"], player_turn["id"],
                                               new_position_box, dice_value)

    assert player_new_position_response.status_code == 400


def test_enter_enclosure_ok():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])

    dice = 6
    possible_movements = roll_dice_and_get_possible_movements(game_response["game"]["id"], player_turn["id"],
                                                              dice).json()

    enclosure_box_id = get_enclosure_box_id(possible_movements)

    move_player(game_response["game"]["id"], player_turn["id"], enclosure_box_id, dice)

    player_in_enclosure_response = enclosure_enter(game_response["game"]["id"], player_turn["id"])

    assert player_in_enclosure_response.status_code == 200
    player_in_enclosure_json = player_in_enclosure_response.json()
    assert player_in_enclosure_json["game"]
    assert player_in_enclosure_json["game"]["id"] == game_response["game"]["id"]
    assert player_in_enclosure_json["player"]["id"] == player_turn["id"]
    assert not player_in_enclosure_json["player"]["current_position"]
    assert player_in_enclosure_json["player"]["enclosure"]


def test_enter_enclosure_wrong_box_fail():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])

    dice = 1
    possible_movements = set(roll_dice_and_get_possible_movements(game_response["game"]["id"], player_turn["id"],
                                                                  dice).json())

    move_player(game_response["game"]["id"], player_turn["id"], possible_movements.pop(), dice)

    player_in_enclosure_response = enclosure_enter(game_response["game"]["id"], player_turn["id"])

    assert player_in_enclosure_response.status_code == 400


def test_exit_enclosure_ok():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])
    dice = 6
    enclosure_box_id = get_enclosure_by_game_id_and_player_id(game_response["game"]["id"], player_turn["id"], dice)

    move_player(game_response["game"]["id"], player_turn["id"], enclosure_box_id, dice)

    player_in_enclosure = enclosure_enter(game_response["game"]["id"], player_turn["id"]).json()
    exit_door = player_in_enclosure["player"]["enclosure"]["doors"][0]["id"]

    player_out_enclosure_response = enclosure_exit(game_response["game"]["id"], player_turn["id"], exit_door)

    assert player_out_enclosure_response.status_code == 200
    player_out_enclosure_json = player_out_enclosure_response.json()
    assert player_out_enclosure_json["game"]
    assert player_out_enclosure_json["game"]["id"] == game_response["game"]["id"]
    assert player_out_enclosure_json["player"]["id"] == player_turn["id"]
    assert player_out_enclosure_json["player"]["current_position"]
    assert not player_out_enclosure_json["player"]["enclosure"]

    with db_session:
        player = find_player_by_id(player_turn["id"])
        assert player
        assert player.game
        assert player.current_position
        assert player.current_position.id == player_out_enclosure_json["player"]["current_position"]["id"]
        assert not player.enclosure


def test_exit_enclosure_wrong_box_fail():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])
    dice = 6
    enclosure_box_id = get_enclosure_by_game_id_and_player_id(game_response["game"]["id"], player_turn["id"], dice)

    move_player(game_response["game"]["id"], player_turn["id"], enclosure_box_id, dice)

    enclosure_enter(game_response["game"]["id"], player_turn["id"]).json()

    player_out_enclosure_response = enclosure_exit(game_response["game"]["id"], player_turn["id"], 1)

    assert player_out_enclosure_response.status_code == 400


def test_accuse_ok():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])
    game_id = game_response["game"]["id"]
    with db_session:
        envelop = get_envelop(game_id)
    accuse_response_ok = accuse(game_id, player_turn["id"], envelop[0], envelop[1], envelop[2])
    assert accuse_response_ok.status_code == 200

    accuse_response_ok_json = accuse_response_ok.json()
    assert accuse_response_ok_json["player_win"] is not None
    assert accuse_response_ok_json["player_win"]["id"] == player_turn["id"]
    assert accuse_response_ok_json["game"]["id"] == game_id
    assert accuse_response_ok_json["cards"] in envelop


def test_accuse_wrong():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])
    game_id = game_response["game"]["id"]
    with db_session:
        envelop = get_envelop(game_id)
    if envelop[0] == 1:
        envelop[0] = 2
    else:
        envelop[0] = envelop[0] - 1
    accuse_cards = envelop
    accuse_response_wrong = accuse(game_id, player_turn["id"], accuse_cards[0], accuse_cards[1], accuse_cards[2])
    assert accuse_response_wrong.status_code == 200

    accuse_response_wrong_json = accuse_response_wrong.json()
    assert accuse_response_wrong_json["player_win"] is None
    assert accuse_response_wrong_json["game"]["id"] == game_id
    assert accuse_response_wrong_json["cards"] in accuse_cards


def test_accuse_whit_not_started_game():
    game_response = create_game_with_n_players("one", ["two", "three", "four"])
    game_id = game_response["game"]["id"]
    player_id = game_response["players"][0]["id"]
    accuse_response_wrong = accuse(game_id, player_id, 1, 15, 19)
    assert accuse_response_wrong.status_code == 400


def test_accuse_default_winner():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two"])
    game_id = game_response["game"]["id"]
    with db_session:
        envelop = get_envelop(game_id)
    accuse_cards = envelop
    if envelop[0] == 1:
        accuse_cards[0] = 2
    else:
        accuse_cards[0] = envelop[0] - 1
    accuse_response_wrong = accuse(game_id, player_turn["id"], accuse_cards[0], accuse_cards[1], accuse_cards[2])
    assert accuse_response_wrong.status_code == 200
    player_win = next(filter(lambda p: p["order"] == 2, game_response["players"]), None)

    accuse_response_wrong_json = accuse_response_wrong.json()
    assert accuse_response_wrong_json["player_win"] is not None
    assert accuse_response_wrong_json["player_win"]["id"] == player_win["id"]
    assert accuse_response_wrong_json["game"]["id"] == game_id
    assert accuse_response_wrong_json["cards"] in envelop


def test_execute_witch_ok():
    game= new_game("nickname").json()
    join_p= join_game(game["game"]["name"],"mickname2").json()
    game_started=start_game(game["game"]["id"],game["player"]["id"]).json()
    player1= find_player_by_id(game["player"]["id"])
    player2= find_player_by_id(join_p["player"]["id"])
    if player1.witch:
         exec_witch= put_execute_witch(game["game"]["id"],game["player"]["id"])
    else:
        exec_witch= put_execute_witch(join_p["game"]["id"], join_p["player"]["id"])
    player1= find_player_by_id(game["player"]["id"])
    player2= find_player_by_id(join_p["player"]["id"])
    assert not player1.witch
    assert not player2.witch
    assert exec_witch.json()
    assert exec_witch.status_code == 200


def test_suspect_ok():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])

    dice = 6
    possible_movements = roll_dice_and_get_possible_movements(game_response["game"]["id"], player_turn["id"],
                                                              dice).json()

    enclosure_box_id = get_enclosure_box_id(possible_movements)

    move_player(game_response["game"]["id"], player_turn["id"], enclosure_box_id, dice)

    enclosure_enter(game_response["game"]["id"], player_turn["id"])
    game_id = game_response["game"]["id"]

    with db_session:
        envelop = get_envelop(game_id)
    suspect_cards = envelop
    if envelop[0] == 1:
        suspect_cards[0] = 2
    else:
        suspect_cards[0] = envelop[0] - 1
    suspect_response = suspect(game_id, player_turn["id"],suspect_cards[1], suspect_cards[2])

    assert suspect_response.status_code == 200


def test_pass_turn_ok():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])
    pass_turn_response = pass_turn(game_response["game"]["id"], player_turn["id"])

    assert pass_turn_response.status_code == 204

def test_pass_turn_wrong():
    game_response, player_turn = create_started_game_and_get_player_turn("one", ["two", "three", "four"])
    for player in game_response["players"]:
        if(player["id"] != player_turn["id"]):
            wrong_player_pass_turn = player["id"]
    pass_turn_response = pass_turn(game_response["game"]["id"], wrong_player_pass_turn)

    assert pass_turn_response.status_code == 400