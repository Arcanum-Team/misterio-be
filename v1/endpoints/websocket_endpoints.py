import json
from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import WebSocket, APIRouter
from starlette.endpoints import WebSocketEndpoint

from core import logger, LiveGameRoom
from core.repositories import find_complete_game

websocket_router = APIRouter()


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
        game_rooms: Dict[UUID, LiveGameRoom] = self.scope.get("games")
        if game_rooms is None:
            raise RuntimeError(f"Global `Game Rooms` instance unavailable!")

        room: LiveGameRoom = game_rooms.get(self.game_id)
        if room is None:
            room = LiveGameRoom()

        await websocket.accept()

        room.add_player(self.player_id, self.game_id, websocket)
        self.scope.get("games")[self.game_id] = room

        game = find_complete_game(self.game_id)

        await room.broadcast_json_message("JOIN_PLAYER", json.loads(game.json()))

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

        room.broadcast_player_left(self.player_id)

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

        await room.broadcast_message(str(msg))

