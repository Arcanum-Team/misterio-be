from fastapi.testclient import TestClient
from v1.endpoints.games_endpoint import games_router 
from v1.endpoints.cards_endpoints import cards_router
from v1.endpoints.board_endpoint import board_router
from uuid import UUID
import main
from core.repositories.games_repository import find_game_by_name
from core.repositories.player_repository import find_player_by_id
from core.services.game_service import find_game_hide_player_id
from pony.orm import db_session 
import logging
import json
from logging.config import dictConfig

game_info= {}
player2_id= ''

game_client = TestClient(games_router)

def test_get_game():
    response = game_client.get("/",
    headers={'accept': 'application/json'}) 
    assert response.status_code == 200
    assert response.json()==[]


def test_post_games():
    global game_info
    response = game_client.post("/",
    headers={'accept': 'application/json', 'Content-Type': 'application/json'},
    json={
        "game_name": "strin5",
        "nickname": "string"
        })
    game_info= response.json()
    with db_session:
        game= find_game_by_name("strin5")
        player= find_player_by_id(game_info["player"]["id"])
    assert response.status_code == 201
    assert response.json()=={
        "game": {
            "name": game.name,
            "player_count": 1,
            "started": game.started,
            "id": str(game.id),
            "turn": game.turn
        },
        "player": {
            "id": str(player.id),
            "nickname": player.nickname,
            "order": player.order,
            "witch": player.witch,
            "host": player.host,
            "current_position": player.current_position,
            "enclosure": player.enclosure
        }
}
    

''' def test_post_games_error():
    response = game_client.post("/",
    headers={'accept': 'application/json', 'Content-Type': 'application/json'},
    json={
        "game_name": "strin5",
        "nickname": "string"
    })
    assert response.status_code==400
    assert response.json()== {
        "message": "Duplicated Game!",
        "path": "/api/v1/games/"
    } '''


def test_put_games_join():
    global player2_id
    response = game_client.put("/join",
        headers={'accept': 'application/json', 'Content-Type': 'application/json'},
        json={"game_name": "strin5",
            "nickname": "string"
    })
    with db_session:
        game= find_game_by_name("strin5")
        player= find_player_by_id(response.json()["player"]["id"])
        player2_id= response.json()["player"]["id"]
    assert response.status_code == 200
    assert response.json()=={
        "game": {
            "name": game.name,
            "player_count": 2,
            "started": game.started,
            "id": str(game.id),
            "turn": game.turn
        },
        "player": {
            "id": str(player.id),
            "nickname": player.nickname,
            "order": player.order,
            "witch": player.witch,
            "host": player.host,
            "current_position": player.current_position,
            "enclosure": player.enclosure
        }
    }

'''
def test_get_games_id():
    global game_info
    id= game_info['game']['id']
    response = game_client.get("/"+id,
    headers={'accept': 'application/json'})
    with db_session:
        game= find_game_hide_player_id(id)
        assert response.status_code == 200
        assert response.json()==json.dumps(game.__dict__)
'''


def test_put_games_start():
    global game_info, player2_info
    response = game_client.put("/start",
        headers={'accept': 'application/json', 'Content-Type': 'application/json'}, 
        json= {
            "game_id": game_info['game']['id'],
            "player_id": game_info['player']['id']
        })
    with db_session:
        game= find_game_by_name("strin5")
        player1= find_player_by_id(response.json()["players"][0]["id"])
        player2= find_player_by_id(response.json()["players"][1]["id"])
        
    assert response.status_code == 200
    assert response.json()=={
        "game": {
            "name": game.name,
            "player_count": 2,
            "started": game.started,
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
            "current_position": {
                "id": player2.current_position.id,
                "attribute": "ENTRY"
            },
            "enclosure": player2.enclosure
            }
        ]
    }



'''
def test_put_games_pass_turn():
    global game_info
    response = game_client.put("/pass_turn",
        headers={'accept': 'application/json',
            'Content-Type': 'application/json'}, 
        json= {
            "game_id": game_info['game']['id']
        })
    assert response.status_code == 200


# cards
card_client = TestClient(cards_router)

def test_get_all_cards():
    response = card_client.get("/",
    headers={'accept': 'application/json'}) # aca va el path si es un get, put o post
    assert response.status_code == 200


def test_get_payer_cards():
    global game_info
    id = game_info['player']['id']
    response = card_client.get("/"+id,
    headers={'accept': 'application/json'}) # aca va el path si es un get, put o post
    assert response.status_code == 200
'''




