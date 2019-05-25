from threading import Thread, RLock
from multiprocessing import Manager
from queue import Queue
from json import load, loads
import time
import os

from uuid import uuid4
import eventlet
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

new_q = Queue() # New host queue
inp_q = Queue() # Input queue
room_lock = RLock()
rooms = {} # Dictionary of 'rooms' aka GameThreads
app = Flask(__name__)
sockets = SocketIO(app) # SocketIO, started in page worker
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
        print(f"New host {hid}")
        with room_lock:
            if len(rooms) < THREADS_LIMIT:
                uid = str(base62.encode(uuid4().int))
                join_room(uid)
                new_q.put(uid)
            else:
                print("Warning: maximum capacity reached for game threads")

    @sockets.on("join")
    def join(data):
        """
        Handle player joining room. Data should be an object with:
            room - Room ID to join.
        """
        try:
            room_id = str(data["room"])
            with room_lock:
                if room_id not in rooms:
                    return False
            join_room(room_id)
            board_id = request.sid
            ret_data = {
                "room": room_id,
                "bid": board_id
            }
            print(f"Player joined room: {ret_data}")

            # Add to room
            with room_lock:
                room = rooms[room_id]
                room.boards[board_id] = room.new_board()
                if len(room.boards) >= 2:
                    print(f"Sending start signal to {room_id}")
                    room.state_q.put("start")
        except Exception as e:
            print(f"An error occurred on join {e}")

    @sockets.on("leave")
    def leave(data):
        """
        Handle player leaving room. Data should be an object with:
            room - Room ID to leave.
            bid - Board ID.
        """
        try:
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
            room = formatted["room"]
            board_id = formatted["bid"]
            command = formatted["command"]
            print(f"Input: {str(formatted)} from {board_id}")
            inp_q.put(formatted)
        except Exception as err:
            print(f"Input error: {err}")
    
    sockets.run(app, port=os.environ.get("PORT", 33507), log_output=False,
        host="0.0.0.0")


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
        self.state_q = state_q if state_q else Queue()
        self.input_q = input_q if input_q else Queue()
        self.running = False # Game active?

    def new_board(self) -> Board:
        return Board(10, 20, self._blocks, self._frames)

    def board_update(self):
        """Update all player boards.
        Returns list of dictionary of board IDs and their raw grid data. REady
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
                print(f"({self.name}) Received start in state queue")
                self.polling = False
                self.start_game()
                break
        self.destroy()

    def performInput(self, inp):
        """Add an input command to the input queue."""
        input_q.put(inp)

    def start_game(self):
        sockets.emit("start", room=self.name)
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
        print(f"New host ID in queue: {hid}")
        with room_lock:
            if len(rooms) < THREADS_LIMIT:
                game_thread = GameThread(None, None, blocks, frames)
                game_thread.name = hid
                game_thread.expire_time = time.perf_counter() + EXPIRE_TIME
                rooms[hid] = game_thread
                game_thread.start()
                sockets.emit("host greet",
                    {"room_id": hid},
                    room=hid,
                    namespace="/host")
                print(f"Started new game thread with ID {hid}")
            else:
                print("Warning: maximum capacity reached for game threads")


def inputWorker():
    """Distribute the inputs to their respective room and boards.
    Expected input format (JSON blob).
    {
        "room": String,
        "bid": String,
        "command": String
    }
    """
    print("Starting input worker...")
    while True:
        inp = inp_q.get()
        print(f"Got input {inp}")
        with room_lock:
            if inp["room"] in rooms:
                rooms[inp["room"]].boards[inp["bid"]].performInput(inp["command"])


page_thread = Thread(target=pageWorker, name="page")
handler_thread = Thread(target=restartingThread, name="handler")
input_thread = Thread(target=inputWorker, name="input")
kill_thread = Thread(target=deadCheckWorker, name="killer")
page_thread.start()
handler_thread.start()
input_thread.start()
kill_thread.start()
