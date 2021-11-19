from fastapi.testclient import TestClient
from v1.endpoints.games_endpoint import games_router 
from v1.endpoints.cards_endpoints import cards_router
from v1.endpoints.board_endpoint import board_router
from uuid import UUID
import main
from core.repositories.games_repository import find_game_by_name
from pony.orm import db_session 
import logging
from logging.config import dictConfig

game_info={}

game_client = TestClient(games_router)

def test_get_game():
    response = game_client.get("/",
    headers={'accept': 'application/json'}) # aca va el path si es un get, put o post
    assert response.status_code == 200


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
    assert response.status_code == 201
    

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
    response = game_client.put("/join",
        headers={'accept': 'application/json', 'Content-Type': 'application/json'},
        json={"game_name": "strin5",
            "nickname": "string"
    })
    assert response.status_code == 200


def test_get_games_id():
    global game_info
    id=game_info['game']['id']
    response = game_client.get("/"+id,
    headers={'accept': 'application/json'})
    assert response.status_code == 200


def test_put_games_start():
    global game_info
    response = game_client.put("/start",
        headers={'accept': 'application/json', 'Content-Type': 'application/json'}, 
        json= {
            "game_id": game_info['game']['id'],
            "player_id": game_info['player']['id']
    })
    assert response.status_code == 200


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





