from tests.util_functions import get_all_cards_endpoint, new_game, join_game, start_game, get_cards_by_player_id


def test_get_all_cards():
    response = get_all_cards_endpoint()
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
