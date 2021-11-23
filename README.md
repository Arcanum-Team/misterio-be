# Misterio API

## Descripción
API server para el juego El Misterio

## Prerequisitos
python3 -m venv venv
source venv/bin/activate
pony==0.7.14
fastapi==0.70.0
"uvicorn[standard]"  #0.15.0
pydantic~=1.8.2
numpy~=1.21.4
starlette~=0.16.0

## Despliegue

### Ambiente de desarrollo

- Abrir la terminal
- Eejcutar: `cd <base_path_misterio_api>`
- Ejecutar: `uvicorn main:app --reload`

### Link Documentación
[LOCAL SWAGGER DOC](http://127.0.0.1:8000/docs)

