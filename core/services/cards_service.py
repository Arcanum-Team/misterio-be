from core.exceptions import MysteryException
from core.repositories import find_player_by_id


def get_cards_by_player_id(player_id):
    player_by_id = find_player_by_id(player_id)
    if not player_by_id.cards:
        raise MysteryException(message="This player doesn't have any cards assigned yet!", status_code=400)
