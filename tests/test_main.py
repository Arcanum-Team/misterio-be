from fastapi.testclient import TestClient
from v1.endpoints.games_endpoint import games_router 
#importar desde donde se quiere testear el objeto creado a partir de FastAPI
from uuid import UUID
import main

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
    assert response.status_code == 201

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
        "player_id": game_info['id']
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
