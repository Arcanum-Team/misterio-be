from tests.util_functions import get_board_endpoint


def test_get_board():
    response = get_board_endpoint()
    assert response.status_code == 200
    json_response = response.json()
    for row in json_response:
        assert row
        assert row["id"]
        assert row["boxes"]
        assert len(row["boxes"]) == 20
