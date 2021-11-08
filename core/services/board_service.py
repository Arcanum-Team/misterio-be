from typing import List

from core.repositories import get_complete_row
from core.schemas import RowOutput


def get_complete_board():
    result: List[RowOutput] = list()
    for i in range(1, 5):
        result.append(RowOutput(id=i, boxes=get_complete_row(i)))

    return result

