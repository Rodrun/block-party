from threading import Queue, Thread

import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets

from game import playfield

# Queues
input_q = Queue()
output_q = Queue()



# Create a Redis channel for a board
class BoardHandle:

    def __init__(self):
        self.field = playfield.PlayField()
        self.score = 0

    def perform(self, name: str):
        """Perform a given input.
        name - Name of input, invalid inputs are ignored.
        """
        if name == "hard":
            # Hard drop
            pass
        else:
            self.field.step()
# Start the playfield channel
# Route websocket for player input
# Route websocket for board output
