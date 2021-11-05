from pydantic.main import BaseModel


class CardBasicInfo(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        orm_mode = True
