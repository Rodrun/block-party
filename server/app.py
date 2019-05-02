from server import namespace
from game.board import Board, GameInput


class Server(socketio.Server):

    def __init__(self, config: dict):
        super().__init__()
        self._config = config
        self._nspace = None

    def set_namespace(self, ns: socketio.Namespace):
        self.register_namespace(ns)

    def poll(self, player: int) -> GameInput:
        """Poll queued player events."""
        pass