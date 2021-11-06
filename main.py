from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from core.exceptions import MysteryException
from core.models import db
from pony.orm import *
from fastapi import FastAPI

from core.settings import settings
from v1.api import api_router
from v1.endpoints import GamesEventMiddleware

app = FastAPI()

db.bind(settings.DB_PROVIDER, 'example.sqlite', create_db=True)  # Conectamos el objeto `db` con la base de datos.
db.generate_mapping(create_tables=True)  # Generamos las base de datos.
set_sql_debug(True)

app.include_router(api_router, prefix=settings.API_V1_STR)


class ErrorContent(BaseModel):
    message: str
    path: str


@app.exception_handler(MysteryException)
async def unicorn_exception_handler(request: Request, exc: MysteryException):
    content = ErrorContent(message=exc.message, path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(content)
    )


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GamesEventMiddleware)
