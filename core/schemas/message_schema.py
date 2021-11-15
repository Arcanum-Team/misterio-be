from typing import List
from uuid import UUID, uuid4
from pydantic.main import BaseModel


class DataMessage(BaseModel):
    player_id: UUID
    game_id: UUID


class DataAccuse(DataMessage):
    result: bool
    cards: List[int]


class DataRoll(DataMessage):
    dice: int


class Message(BaseModel):
    type: str
    data: DataMessage

# d = DataAccuse(player_id = uuid4(), result = True, cards = [1])
# m = Message(type = "accuse", data = d)
# print(m.json())
