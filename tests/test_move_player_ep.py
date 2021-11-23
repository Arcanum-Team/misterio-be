import random

from pony.orm import db_session

from core.repositories import find_player_by_id
from tests.common_endpoints import move_player, create_started_game_and_get_player_turn, \
    roll_dice_and_get_possible_movements


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



