from typing import List, Optional
from uuid import UUID
from pydantic.main import BaseModel


class DataMessage(BaseModel):
    player_id: UUID
    game_id: UUID


class DataSuspectNotice(DataMessage):
    reached_player_id: Optional[UUID]
    monster_id: int
    victim_id: int
    enclosure_id: int


class DataSuspectRequest(DataMessage):
    monster_id: int
    victim_id: int
    enclosure_id: int


class DataSuspectResponse(BaseModel):
    card: Optional[int]


class DataAccuse(DataMessage):
    result: bool
    cards: List[int]


class DataRoll(DataMessage):
    dice: int


class Message(BaseModel):
    type: str
    data: DataMessage
