from core.models import db
from pony.orm import *
from fastapi import FastAPI

from core.settings import settings
from v1.api import api_router

app = FastAPI()

db.bind(settings.DB_PROVIDER, 'example.sqlite', create_db=True)  # Conectamos el objeto `db` con la base de datos.
db.generate_mapping(create_tables=True)  # Generamos las base de datos.
set_sql_debug(True)

app.include_router(api_router, prefix=settings.API_V1_STR)
