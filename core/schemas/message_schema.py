from typing import List, Optional
from uuid import UUID
from pydantic.main import BaseModel

from core.schemas.player_schema import PlayerOutput, GamePlayer


class DataMessage(BaseModel):
    player_id: UUID
    game_id: UUID


class DataSuspectNotice(DataMessage):
    reached_player_id: Optional[UUID]
    monster_id: int
    victim_id: int
    enclosure_id: int


class DataSuspectResponse(BaseModel):
    card: Optional[int]


class DataAccuse(GamePlayer):
    cards: List[int]
    player_win: Optional[PlayerOutput]
    next_player_turn: Optional[PlayerOutput]


class DataRoll(DataMessage):
    dice: int

class DataChatMessage(BaseModel):
    game_id: UUID
    nickname: str
    message: str


class Message(BaseModel):
    type: str
    data: DataMessage
