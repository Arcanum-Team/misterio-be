from fastapi.testclient import TestClient
from v1.endpoints.games_endpoint import games_router #importar desde donde se quiere testear el objeto creado a partir de FastAPI

game_client = TestClient(games_router)


def test_read_main():
    response = game_client.get("/",
    headers={'accept': 'application/json'}) # aca va el path si es un get, put o post
    assert response.status_code == 200
