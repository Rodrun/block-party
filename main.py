from threading import Thread, RLock
from multiprocessing import Manager
from queue import Queue
from json import load, loads
import time

from uuid import uuid4
import eventlet
from flask import Flask, Blueprint, send_from_directory, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
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

    @sockets.on("host")
    def host():
        hid = request.sid
        print(f"New host {hid}")
        #new_q.put(hid)
        #sockets.emit("host greet", { "room_id": hid })
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
            sockets.emit("joined room", ret_data)
            print(f"Player joined room: {ret_data}")
            with room_lock:
                if len(rooms[room_id].boards) >= 2:
                    rooms[room_id].state_q.put("start")
        except:
            print("An error occurred on join")
            return False

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
        except:
            print("Error occurred when leaving room.")

    @sockets.on("input")
    def inp(msg):
        try:
            formatted = loads(msg)
            room = formatted["room"]
            board_id = request.namespace.socket.sessid
            command = formatted["command"]
            formatted["bid"] = request.namespace.socket.sessid
            formatted["new"] = True
            print(f"Input: {str(formatted)} from {board_id}")
            #with games:
            #   games[room].boards[board_id].performInput(command)
            inp_q.put(formatted)
        except:
            pass
    
    sockets.run(app, port="8080", log_output=False)


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
        self.boards = {} # Keys will be client socket sessid
        self.state_q = state_q if state_q else Queue()
        self.input_q = input_q if input_q else Queue()
        self.running = False # Game active?

    def new_board(self) -> Board:
        return Board(10, 20, self._blocks, self._frames)

    def board_update(self):
        for b in self.boards:
            b.update(1 / 60)

    def run(self):
        while self.polling:
            if self.state_q.get() == "start":
                print(f"({self.name}) Received start in state queue")
                self.polling = False
        self.start_game()

    def performInput(self, inp):
        """Add an input command to the input queue."""
        input_q.put(inp)

    def start_game(self):
        sockets.emit("start", room=self.name)
        self.running = True
        while self.running and len(self.boards) == 2:
            try:
                if self.state_q.get_nowait() == "stop":
                    print(f"({self.name}) Received stop in state queue")
                    self.running = False
                for i in range(INPUT_LIMIT):
                    inp = self.input_q.get_nowait()
                    self.boards[inp[0]].performInput(inp[1])
            except:
                pass
            self.board_update()
            for b in self.boards:
                self.running = not b.has_lost()
            
            # Send grid data of both boards
            grid_data = {}
            time.sleep(.016)
        self.destroy()

    def destroy(self):
        self.polling = False
        print(f"({self.name}) Ending.")
        self.join()


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
                    rooms[key].polling = False
                    del rooms[key]

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
                sockets.emit("host greet", {"room_id": hid}, room=hid)
                print(f"Started new game thread with ID {hid}")
            else:
                print("Warning: maximum capacity reached for game threads")


def inputWorker():
    """Distribute the inputs to their respective room and boards."""
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
