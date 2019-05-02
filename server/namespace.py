import socketio


class Doubles(socketio.Namespace):
    """
    1v1 namespace. Keeps track of two sockets at most.
    """

    def __init__(self, name: str = "/"):
        super().__init__(name)
        self._count = 0 # Connected player count

    def on_connect(self, sid, environ):
        if self.game_ready():
            return False
        self._count += 1
        serv.save_session(sid,
            {
                "name": "Player " + str(self._count),
                "queue": [] # Input queue
            })
        self.log(sid, "connect.")

    def on_disconnect(self, sid):
        if sid in self._pids:
            self._pids.discard(sid)
            self.log(sid, "disconnect.")

    def on_input(self, sid, data):
        with get_session(sid) as session:
            session["queue"].append(data)

    def log(self, sid, msg):
        print(f"{socketio.get_session(sid)["name"]} ({sid}): {msg}")

    def game_ready(self) -> bool:
        """Check if two players are connected."""
        return len(self._pids) == 2
