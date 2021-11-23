from fastapi.testclient import TestClient
from v1.endpoints.games_endpoint import games_router
from v1.endpoints.cards_endpoints import cards_router
from v1.endpoints.board_endpoint import board_router
from core.repositories.games_repository import find_game_by_name
from core.repositories.player_repository import find_player_by_id
from core.services.board_service import get_complete_board
from core.services.shifts_service import get_possible_movement
from pony.orm import db_session
from core.repositories.games_repository import find_player_by_turn
from v1.endpoints.shifts_endpoint import shifts_router
from core.models.board_model import Enclosure, Box
import main
game_info = {}
player2_id = ''

game_client = TestClient(games_router)


def test_get_game():
    response = game_client.get("/",
                               headers={'accept': 'application/json'})
    assert response.status_code == 200
    assert response.json() == []


def test_post_games():
    global game_info
    response = game_client.post("/",
                                headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                                json={
                                    "game_name": "strin5",
                                    "nickname": "string"
                                })
    game_info = response.json()
    with db_session:
        game = find_game_by_name("strin5")
        player = find_player_by_id(game_info["player"]["id"])
    assert response.status_code == 201
    assert response.json() == {
        "game": {
            "name": game.name,
            "player_count": 1,
            "started": game.started,
            "has_password": None,
            "id": str(game.id),
            "turn": game.turn
        },
        "player": {
            "id": str(player.id),
            "nickname": player.nickname,
            "order": player.order,
            "witch": player.witch,
            "host": player.host,
            "loser": player.loser,
            "color": player.color,
            "current_position": player.current_position,
            "enclosure": player.enclosure
        }
    }


def test_put_games_join():
    global player2_id
    response = game_client.put("/join",
                               headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                               json={"game_name": "strin5",
                                     "nickname": "string"
                                     })
    with db_session:
        game = find_game_by_name("strin5")
        player = find_player_by_id(response.json()["player"]["id"])
        player2_id = response.json()["player"]["id"]
    assert response.status_code == 200
    assert response.json() == {
        "game": {
            "name": game.name,
            "player_count": 2,
            "started": game.started,
            "has_password": None,
            "id": str(game.id),
            "turn": game.turn
        },
        "player": {
            "id": str(player.id),
            "nickname": player.nickname,
            "order": player.order,
            "witch": player.witch,
            "host": player.host,
            "loser": player.loser,
            "color": player.color,
            "current_position": player.current_position,
            "enclosure": player.enclosure
        }
    }


def test_get_games_id():
    global game_info
    id = game_info['game']['id']
    response = game_client.get("/" + id,
                               headers={'accept': 'application/json'})
    assert response.status_code == 200


def test_put_games_start():
    global game_info
    response = game_client.put("/start",
                               headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                               json={
                                   "game_id": game_info['game']['id'],
                                   "player_id": game_info['player']['id']
                               })
    with db_session:
        game = find_game_by_name("strin5")
        player1 = find_player_by_id(response.json()["players"][0]["id"])
        player2 = find_player_by_id(response.json()["players"][1]["id"])

    assert response.status_code == 200
    assert response.json() == {
        "game": {
            "name": game.name,
            "player_count": 2,
            "started": game.started,
            "has_password": None,
            "id": str(game.id),
            "turn": game.turn
        },
        "players": [
            {
                "id": str(player1.id),
                "nickname": player1.nickname,
                "order": player1.order,
                "witch": player1.witch,
                "host": player1.host,
                "loser": player1.loser,
                "color": player1.color,
                "current_position": {
                    "id": player1.current_position.id,
                    "attribute": "ENTRY"
                },
                "enclosure": player1.enclosure
            },
            {
                "id": str(player2.id),
                "nickname": player2.nickname,
                "order": player2.order,
                "witch": player2.witch,
                "host": player2.host,
                "loser": player2.loser,
                "color": player2.color,
                "current_position": {
                    "id": player2.current_position.id,
                    "attribute": "ENTRY"
                },
                "enclosure": player2.enclosure
            }
        ]
    }


# cards
card_client = TestClient(cards_router)


def test_get_all_cards():
    response = card_client.get("/",
                               headers={'accept': 'application/json'})
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "COCHERA",
            "type": "ENCLOSURE"
        },
        {
            "id": 2,
            "name": "ALCOBA",
            "type": "ENCLOSURE"
        },
        {
            "id": 3,
            "name": "BIBLIOTECA",
            "type": "ENCLOSURE"
        },
        {
            "id": 4,
            "name": "VESTIBULO",
            "type": "ENCLOSURE"
        },
        {
            "id": 5,
            "name": "PANTEON",
            "type": "ENCLOSURE"
        },
        {
            "id": 6,
            "name": "BODEGA",
            "type": "ENCLOSURE"
        },
        {
            "id": 7,
            "name": "SALON",
            "type": "ENCLOSURE"
        },
        {
            "id": 8,
            "name": "LABORATORIO",
            "type": "ENCLOSURE"
        },
        {
            "id": 9,
            "name": "DRACULA",
            "type": "MONSTER"
        },
        {
            "id": 10,
            "name": "FRANKENSTEIN",
            "type": "MONSTER"
        },
        {
            "id": 11,
            "name": "HOMBRE LOBO",
            "type": "MONSTER"
        },
        {
            "id": 12,
            "name": "FANTASMA",
            "type": "MONSTER"
        },
        {
            "id": 13,
            "name": "MOMIA",
            "type": "MONSTER"
        },
        {
            "id": 14,
            "name": "DR. JEKYLL MR. HYDE",
            "type": "MONSTER"
        },
        {
            "id": 15,
            "name": "CONDE",
            "type": "VICTIM"
        },
        {
            "id": 16,
            "name": "CONDESA",
            "type": "VICTIM"
        },
        {
            "id": 17,
            "name": "AMA DE LLAVES",
            "type": "VICTIM"
        },
        {
            "id": 18,
            "name": "MAYORDOMO",
            "type": "VICTIM"
        },
        {
            "id": 19,
            "name": "DONCELLA",
            "type": "VICTIM"
        },
        {
            "id": 20,
            "name": "JARDINERO",
            "type": "VICTIM"
        }
    ]


def test_get_player_cards():
    global game_info
    id = game_info['player']['id']
    response = card_client.get("/" + id,
                               headers={'accept': 'application/json'})
    with db_session:
        player = find_player_by_id(id)
        cards_list = [{"id": card.id, "name": card.name, "type": card.type} for card in player.cards]
    assert response.status_code == 200
    same_cards = True
    for i in response.json():
        if i not in cards_list:
            same_cards = False
            break
    assert same_cards


# Board
board_client = TestClient(board_router)


def test_get_board():
    response = board_client.get("/",
                                headers={'accept': 'application/json'})
    board = get_complete_board()
    assert response.status_code == 200


def test_get_adjacent():
    response = board_client.get("/box/adj/4/3",
                                headers={'accept': 'application/json'})
    board = get_possible_movement(3, 4)
    assert response.status_code == 200
    assert response.json() == list(board)


# Shifts
shift_client = TestClient(shifts_router)


def test_put_games_suspect():
    global game_info
    with db_session:
        game = find_game_by_name("strin5")
        player_by_turn = find_player_by_turn(game.players, game.turn)
        player_turn = find_player_by_id(player_by_turn.id)
        player_turn.enclosure = Enclosure[2]
    response = shift_client.put("/suspect",
                                headers={'accept': 'application/json',
                                         'Content-Type': 'application/json'},
                                json={
                                    "game_id": str(game.id),
                                    "player_id": str(player_turn.id),
                                    "monster_id": 10,
                                    "victim_id": 19
                                }
                                )
    assert response.status_code == 200


def test_put_send_suspect_card():
    global game_info, player2_id
    with db_session:
        game = find_game_by_name("strin5")
        player1 = find_player_by_id(game_info["player"]["id"])
        player2 = find_player_by_id(player2_id)
        for card in player1.cards:
            card_id = card.id
            break
    response = shift_client.put("/send_suspect_card",
                                headers={'accept': 'application/json',
                                         'Content-Type': 'application/json'},
                                json={
                                    "game_id": str(game.id),
                                    "from_player": str(player1.id),
                                    "to_player": str(player2.id),
                                    "card": card_id
                                }
                                )
    assert response.status_code == 200


def test_put_roll_dice():
    global game_info
    response = shift_client.put("/roll-dice",
                                headers={'accept': 'application/json',
                                         'Content-Type': 'application/json'},
                                json={
                                    "game_id": str(game_info["game"]["id"]),
                                    "player_id": str(game_info["player"]["id"]),
                                    "dice": 6
                                }
                                )
    assert response.status_code == 200


def test_put_enclosure_enter():
    global game_info
    with db_session:
        player = find_player_by_id(game_info["player"]["id"])
        player.current_position = Box[45]
    response = shift_client.put("/enclosure/enter",
                                headers={'accept': 'application/json',
                                         'Content-Type': 'application/json'},
                                json={
                                    "game_id": str(game_info["game"]["id"]),
                                    "player_id": str(game_info["player"]["id"])
                                }
                                )
    assert response.status_code == 200
