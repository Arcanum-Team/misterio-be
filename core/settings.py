import logging
from logging.config import dictConfig
from uuid import UUID
from fastapi import WebSocket
from pydantic import BaseSettings, BaseModel
from typing import Optional, Dict, List, Any

from starlette.types import ASGIApp, Scope, Receive, Send


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    DB_PROVIDER: str = "sqlite"
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"

    class Config:
        case_sensitive = True


settings = Settings()


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "mystery_log"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "mystery_log": {"handlers": ["default"], "level": LOG_LEVEL},
    }


dictConfig(LogConfig().dict())

logger = logging.getLogger("mystery_log")


# Web Socket


class LiveGameRoom:
    """Room state, comprising connected players.
    """

    def __init__(self):
        logger.info("Creating new empty room")
        self._players: Dict[UUID, WebSocket] = {}

    def __len__(self) -> int:
        """Get the number of players in the room.
        """
        return len(self._players)

    @property
    def empty(self) -> bool:
        """Check if the room is empty.
        """
        return len(self._players) == 0

    @property
    def player_list(self) -> List[UUID]:
        """Return a list of IDs for connected players.
        """
        return list(self._players.keys())

    def add_player(self, player: UUID, game_id: UUID, websocket: WebSocket):
        """Add a player websocket, keyed by corresponding player ID.

        Raises:
            ValueError: If the `player.id` already exists within the room.
        """
        if player in self._players.keys():
            raise ValueError(f"Player {player} is already in the room")

        logger.info("Adding player [%s] to room game [%s]", player, game_id)

        self._players[player] = websocket

    async def kick_player(self, player_id: UUID):
        """Forcibly disconnect a player from the room.

        We do not need to call `remove_player`, as this will be invoked automatically
        when the websocket connection is closed by the `RoomLive.on_disconnect` method.

        Raises:
            ValueError: If the `player_id` is not held within the room.
        """
        if player_id not in self._players:
            raise ValueError(f"player {player_id} is not in the room")
        await self._players[player_id].send_json(
            {
                "type": "ROOM_KICK",
                "data": {"msg": "You have been kicked from the chatroom!"},
            }
        )
        logger.info("Kicking player %s from room", player_id)
        await self._players[player_id].close()

    def remove_player(self, player_id: UUID):
        """Remove a player from the room.

        Raises:
            ValueError: If the `player_id` is not held within the room.
        """
        if player_id not in self._players:
            raise ValueError(f"player {player_id} is not in the room")
        logger.info("Removing player %s from room", player_id)
        del self._players[player_id]

    async def whisper(self, from_player: UUID, to_player: UUID, msg: str):
        """Send a private message from one player to another.

        Raises:
            ValueError: If either `from_player` or `to_player` are not present
                within the room.
        """
        if from_player not in self._players:
            raise ValueError(f"Calling player {from_player} is not in the room")
        logger.info("player %s messaging player %s -> %s", from_player, to_player, msg)
        if to_player not in self._players:
            await self._players[from_player].send_json(
                {
                    "type": "ERROR",
                    "data": {"msg": f"player {to_player} is not in the game!"},
                }
            )
            return
        await self._players[to_player].send_json(
            {
                "type": "WHISPER",
                "data": {"from_player": from_player, "to_player": to_player, "msg": msg},
            }
        )

    async def broadcast_message(self, message: str):
        """Broadcast message to all connected players.
        """
        for websocket in self._players.values():
            logger.info(f"websocket player: {websocket} message: [{message}]")
            await websocket.send_text(message)

    async def broadcast_json_message(self, message_type: str, data: Any):
        """Broadcast message to all connected players.
        """

        for websocket in self._players.values():
            await websocket.send_json({"type": message_type, "data": data})

    def broadcast_player_left(self, player_id: UUID):
        """Broadcast message to all connected players.
        """
        for websocket in self._players.values():
            websocket.send_json({"type": "player_LEAVE", "data": player_id})

    def message_to_player(self, player_id: UUID, message_type: str, data: Any):
        wb = self._players[player_id]
        wb.send_json({"type": message_type, "data": data})


games: Dict[UUID, LiveGameRoom] = {}


class GamesEventMiddleware:
    """Middleware for providing a global :class:`~.LivingGameRoom` instance to both HTTP
    and WebSocket scopes.

    Although it might seem odd to load the broadcast interface like this (as
    opposed to, e.g. providing a global) this both mimics the pattern
    established by starlette's existing DatabaseMiddlware, and describes a
    pattern for installing an arbitrary broadcast backend (Redis PUB-SUB,
    Postgres LISTEN/NOTIFY, etc) and providing it at the level of an individual
    request.
    """

    def __init__(self, app: ASGIApp):
        self._app = app
        self._games = games

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ("lifespan", "http", "websocket"):
            scope["games"] = self._games
        await self._app(scope, receive, send)


def get_live_game_room(uuid: UUID):
    logger.info(f"web socket games: {games}")
    return games.get(str(uuid))

