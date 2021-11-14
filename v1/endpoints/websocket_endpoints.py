from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import WebSocket, APIRouter
from starlette.endpoints import WebSocketEndpoint
from starlette.types import ASGIApp, Scope, Receive, Send

from core import logger
from core.repositories import find_basic_player
from core.schemas import BasicPlayerInfo, Message

websocket_router = APIRouter()


class LiveGameRoom:
    """Room state, comprising connected players.
    """

    def __init__(self):
        logger.info("Creating new empty room")
        self._players: Dict[UUID, WebSocket] = {}
        self._player_meta: Dict[UUID, BasicPlayerInfo] = {}

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
    def player_list(self) -> List[BasicPlayerInfo]:
        """Return a list of IDs for connected players.
        """
        return list(self._player_meta.values())

    def add_player(self, player: BasicPlayerInfo, game_id: UUID, websocket: WebSocket):
        """Add a player websocket, keyed by corresponding player ID.

        Raises:
            ValueError: If the `player.id` already exists within the room.
        """
        if player.id in self._players:
            raise ValueError(f"Player {player.id} is already in the room")

        logger.info("Adding player [%s] to room game [%s]", player.id, game_id)

        self._players[player.id] = websocket
        self._player_meta[player.id] = player

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
        del self._player_meta[player_id]

    def get_player(self, player_id: UUID) -> Optional[BasicPlayerInfo]:
        """Get metadata on a player.
        """
        return self._player_meta.get(player_id)

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

    async def broadcast_message(self, message:Message):
        """Broadcast message to all connected players.
        """
        for websocket in self._players.values():
            await websocket.send_json(message.json())

    async def broadcast_player_joined(self, player_id: UUID):
        """Broadcast message to all connected players.
        """
        for websocket in self._players.values():
            await websocket.send_json({"type": "player_JOIN", "data": player_id})

    async def broadcast_player_left(self, player_id: UUID):
        """Broadcast message to all connected players.
        """
        for websocket in self._players.values():
            await websocket.send_json({"type": "player_LEAVE", "data": player_id})


games: Dict[UUID, LiveGameRoom] = {}

class GamesEventMiddleware:  # pylint: disable=too-few-public-methods
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


@websocket_router.websocket_route("/{game_id}/{player_id}")
class RoomLive(WebSocketEndpoint):
    """Live connection to the global :class:`~.Room` instance, via WebSocket.
    """

    encoding: str = "text"
    session_name: str = ""
    count: int = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        first_arg: Dict[str, Dict] = args[0]
        path_params: Dict[str, UUID] = first_arg.get('path_params')
        self.player_id: UUID = path_params.get('player_id')
        self.game_id: UUID = path_params.get('game_id')

    async def on_connect(self, websocket):
        """Handle a new connection.

        New players are assigned a player ID and notified of the room's connected
        players. The other connected players are notified of the new player's arrival,
        and finally the new player is added to the global :class:`~.Room` instance.
        """
        logger.info(f"Connecting new player game[{self.game_id}] player[{self.player_id}]")
        game_rooms: Optional[Dict[UUID, LiveGameRoom]] = self.scope.get("games")
        if game_rooms is None:
            raise RuntimeError(f"Global `Game Rooms` instance unavailable!")

        room: LiveGameRoom = game_rooms.get(self.game_id)
        if room is None:
            room = LiveGameRoom()

        await websocket.accept()
        await websocket.send_json(
            {"type": "ROOM_JOIN", "data": {"player_id": self.player_id}}
        )
        await room.broadcast_player_joined(self.player_id)
        room.add_player(find_basic_player(self.player_id), self.game_id, websocket)
        game_rooms[self.game_id] = room

    async def on_disconnect(self, _websocket: WebSocket, _close_code: int):
        """Disconnect the player, removing them from the :class:`~.Room`, and
        notifying the other players of their departure.
        """
        logger.info(f"Disconnect game[{self.game_id}] player[{self.player_id}]")

        if self.player_id is None:
            raise RuntimeError(
                "RoomLive.on_disconnect() called without a valid player_id"
            )
        game_rooms: Optional[Dict[UUID, LiveGameRoom]] = self.scope.get("games")
        room: LiveGameRoom = game_rooms.get(self.game_id)

        if room is None:
            logger.error(f"Invalid game {self.game_id}")
            raise RuntimeError("Invalid Game ")

        room.remove_player(self.player_id)
        if room.empty:
            del game_rooms[self.game_id]

        await room.broadcast_player_left(self.player_id)

    async def on_receive(self, _websocket: WebSocket, msg: Any):
        """Handle incoming message: `msg` is forwarded straight to `broadcast_message`.
        """
        if self.game_id is None:
            raise RuntimeError("RoomLive.on_receive() called without a valid game_id")

        if self.player_id is None:
            raise RuntimeError("RoomLive.on_receive() called without a valid player_id")

        if not isinstance(msg, str):
            raise ValueError(f"RoomLive.on_receive() passed unhandleable data: {msg}")

        game_rooms: Optional[Dict[UUID, LiveGameRoom]] = self.scope.get("games")
        room: LiveGameRoom = game_rooms.get(self.game_id)

        await room.broadcast_message(self.player_id, msg)
