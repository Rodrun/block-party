from threading import Thread, RLock
from multiprocessing import Manager
from queue import Queue
from json import load, loads
import time
import os

#from uuid import uuid4
from shortuuid import uuid
from shortuuid import encode
from flask import Flask, Blueprint, send_from_directory, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit, close_room
import base62

from game.board import Board


THREADS_LIMIT = 225 # Semi-arbitrary limit; Heroku allows 255 threads for free
INPUT_LIMIT = 8 # Maximum inputs to process per tick for a game
BLOCKS_PATH = "config/blocks.json"
FRAMES_PATH = "config/frames.json"
DEAD_TIME = 1 # Seconds to check for dead games
EXPIRE_TIME = 60 * 6 # Seconds until a game can be considered for death,
                     # a game is 'dead' when it has been alive for this amount
                     # of time, and 'running' is False.
NAMES = ["Left Board", "Right Board"]

new_q = Queue() # New host queue
inp_q = Queue() # Input queue
out_q = Queue() # Output queue
room_lock = RLock()
rooms = {} # Dictionary of 'rooms' aka GameThreads
app = Flask(__name__)
sockets = SocketIO(app, async_mode="threading") # SocketIO, started in page worker
html = Blueprint("html", __name__, "static", template_folder="static")


@html.route("/")
def index():
    return send_from_directory("static", "controller.html")


@html.route("/css/<path:path>")
def css(path):
    return send_from_directory("static/css", path)


@html.route("/js/<path:path>")
def js(path):
    return send_from_directory("static/js", path)


@html.route("/host")
def host():
    return send_from_directory("static", "host.html")


@html.route("/music/<path:path>")
def music(path):
    return send_from_directory("static/music", path)


def pageWorker():
    """Static page serving and SocketIO."""
    print("Starting page worker...")
    global sockets
    app.register_blueprint(html, url_prefix="/")
    blocks = load(open(BLOCKS_PATH))
    frames = load(open(FRAMES_PATH))

    @sockets.on("host", namespace="/host")
    def host():
        hid = request.sid
        with room_lock:
            if len(rooms) < THREADS_LIMIT:
                uid = uuid()[:10] # More chance of duplicate
                                  # But 'rare enough'
                join_room(uid)
                new_q.put(uid)
            else:
                print("Warning: maximum capacity reached for game threads")

    @sockets.on("ready", namespace="/host")
    def ready(hid):
        """When the host is ready to begin the match.
        Will only start the match if 2 players have joined.
        Returns (boolean, message) to client, where boolean is True when
        the game is starting.
        """
        with room_lock:
            if not hid in rooms:
                return False, "Invalid room"
            elif len(rooms[hid].boards) < 2:
                return False, "Need 2 players to start"
            else:
                rooms[hid].state_q.put("start")
                return True, "Starting game"

    @sockets.on_error_default
    def all_error_handler(e):
        print(f"SocketIO Error: {e}")

    @sockets.on("join")
    def join(data):
        """
        Handle player joining room. Data should be an object with:
            room - Room ID to join.
        Returns (boolean, message, [bid]) to client. Where the boolean is
        True when the client has successfully joined the room. bid is only
        returned when the client is in the room.
        """
        try:
            data = loads(data)
            room_id = str(data["room"])
            with room_lock:
                if room_id not in rooms:
                    return False, "Invalid Room"
                elif len(rooms[room_id].boards) >= 2:
                    return False, "Full Room"
                join_room(room_id)
                board_id = request.sid
                room = rooms[room_id]
                room.boards[board_id] = room.new_board()
                return True, NAMES[len(room.boards) - 1], board_id
        except Exception as e:
            print(f"An error occurred on join: {e}")
            return False, "Error"

    @sockets.on("leave")
    def leave(data):
        """
        Handle player leaving room. Data should be an object with:
            room - Room ID to leave.
            bid - Board ID.
        """
        try:
            data = loads(data)
            room_id = str(data["room"])
            bid = str(data["bid"])
            leave_room(room_id)
            with room_lock:
                del rooms[room_id].boards[bid]
        except Exception as e:
            print(f"Error occurred when leaving room: {e}")

    @sockets.on("input")
    def inp(msg):
        try:
            formatted = loads(msg)
            formatted["bid"] = request.sid
            #inp_q.put(formatted)
            if not contains(inp, ["room", "bid", "command"]):
                return
            with room_lock:
                if inp["room"] in rooms:
                    rooms[inp["room"]].boards[inp["bid"]].performInput(inp["command"])
        except Exception as err:
            print(f"Input error: {err}")
    
    sockets.run(app, port=os.environ.get("PORT", 33507), log_output=False,
        host="0.0.0.0", debug=False)


class GameThread(Thread):

    def __init__(self, state_q: Queue, input_q: Queue, blocks, frames):
        """
        state_q - Game State Queue (start, stop, etc.).
        input_q - Game Input Queue (from players).
        blocks - Block data.
        Frames - Frame data.
        """
        super().__init__()
        self.name = ""
        self.polling = True # Polling for state_q event
        self.expire_time = 0
        self._blocks = blocks
        self._frames = frames
        self.boards = {} # Keys will be board ID (bid)
        self.losses = 0 # When 2, end game
        self.state_q = state_q if state_q else Queue()
        self.input_q = input_q if input_q else Queue()
        self.running = False # Game active?

    def new_board(self) -> Board:
        return Board(10, 20, self._blocks, self._frames)

    def board_update(self):
        """Update all player boards.
        Returns list of dictionary of board IDs and their raw grid data. Ready
        to send to host client in following JSON format:
        {
            "bid": Str,
            "grid": list
        }
        """
        result = []
        for bid, b in self.boards.items():
            b.update(1 / 60)
            result.append({ "bid": bid, "grid": b.get_raw_grid() })
        return result

    def run(self):
        while self.polling:
            if self.state_q.get() == "start":
                polling = False
                self.start_game()
                break
        self.destroy()

    def performInput(self, inp):
        """Add an input command to the input queue."""
        input_q.put(inp)

    def start_game(self):
        sockets.emit("start game", room=self.name, namespace="/host")
        self.running = True
        current = None # Current frame's grid from update
        last = None # Last frame's grid from update
        while self.running and len(self.boards) >= 2:
            try:
                if self.state_q.get_nowait() == "stop": # Currently unused
                    print(f"({self.name}) Received stop in state queue")
                    self.running = False
                for i in range(INPUT_LIMIT):
                    inp = self.input_q.get_nowait()
                    self.boards[inp[0]].performInput(inp[1])
            except: # get_nowait
                pass

            for bid, b in self.boards.items():
                self.running = not b.has_lost()
                if not self.running:
                    print(f"({self.name}) Player {bid} has lost")
                    break
            # Send new boards
            # TODO: Optimize later
            if current != None:
                last = current[:]
            current = self.board_update()
            if current != last:
                sockets.emit("update", current, room=self.name, namespace="/host")
            time.sleep(.016)

    def destroy(self):
        print(f"({self.name}) Ending.")



def deadCheckWorker():
    """Checks if any game threads are dead and closes them."""
    print("Starting killer worker...")
    while True:
        time.sleep(DEAD_TIME)
        with room_lock:
            current = time.perf_counter()
            for key in list(rooms.keys()):
                if current >= rooms[key].expire_time and not rooms[key].running:
                    print(f"{key} has been inactive, killing...")
                    rooms[key].polling = False # Possible data race?
                    del rooms[key]
                    print(f"Active rooms:\n{list(rooms.keys())}")


def restartingThread():
    """Handles creation of new game threads."""
    print("Starting room worker...")
    blocks = load(open("config/blocks.json"))["blocks"]
    frames = load(open("config/frames.json"))
    while True:
        hid = new_q.get() # Unique room ID as string
        with room_lock:
            if len(rooms) < THREADS_LIMIT:
                game_thread = GameThread(None, None, blocks, frames)
                game_thread.name = hid
                game_thread.expire_time = time.perf_counter() + EXPIRE_TIME
                rooms[hid] = game_thread
                game_thread.start()
                #eventlet.spawn(game_thread.run)
                sockets.emit("host greet",
                    {"room_id": hid},
                    room=hid,
                    namespace="/host")
                #sockets.emit("start game", room=hid, namespace="/host")
            else:
                print("Warning: maximum capacity reached for game threads")


def contains(target: dict, keyList: list) -> bool:
    """Check if all the keys in keyList are in target."""
    for key in keyList:
        if key not in target:
            return False
    return True

page_thread = Thread(target=pageWorker, name="page")
handler_thread = Thread(target=restartingThread, name="handler")
kill_thread = Thread(target=deadCheckWorker, name="killer")
page_thread.start()
handler_thread.start()
kill_thread.start()
