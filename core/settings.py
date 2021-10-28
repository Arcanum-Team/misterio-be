from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator
from typing import List, Optional, Union


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"


    #BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    #@validator("BACKEND_CORS_ORIGINS", pre=True)  # 3
    #def assemble_cors_origins(self, v: Union[str, List[str]]) -> Union[List[str], str]:
    #    if isinstance(v, str) and not v.startswith("["):
    #        return [i.strip() for i in v.split(",")]
    #    elif isinstance(v, (list, str)):
    #        return v
    #    raise ValueError(v)

    DB_PROVIDER: str = "sqlite"
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"

    class Config:
        case_sensitive = True


settings = Settings()
