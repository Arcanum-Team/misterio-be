from fastapi.testclient import TestClient
from v1.endpoints.games_endpoint import games_router #importar desde donde se quiere testear el objeto creado a partir de FastAPI

game_client = TestClient(games_router)


def test_get_game():
    response = game_client.get("/",
    headers={'accept': 'application/json'}) # aca va el path si es un get, put o post
    assert response.status_code == 200

def test_post_games():
    response = game_client.post("/",
    headers={'accept': 'application/json', 'Content-Type': 'application/json'},
    json={
        "game_name": "string",
        "nickname": "string"
        })
    assert response.status_code == 201

def test_put_games_join():
    response = game_client.put("/join",
    headers={'accept': 'application/json', 'Content-Type': 'application/json'},
    json={
        "game_name": "string",
        "nickname": "string"
        })
    assert response.status_code == 200

def test_get_games_id():
    id="c17ff26c-0328-4098-afbf-b0f852e85197"
    response = game_client.get("/{id}",
    headers={'accept': 'application/json'})
    assert response.status_code == 200

def test_put_games_start():
    response = game_client.put("/start",
    headers={'accept': 'application/json', 'Content-Type': 'application/json'}, 
    json= {
        "game_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "player_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        })
    assert response.status_code == 200

def test_put_games_pass_turn():
    response = game_client.put("/pass_turn",
    headers={'accept': 'application/json',
    'Content-Type': 'application/json'}, 
    json= {
        "game_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        })
    assert response.status_code == 200

