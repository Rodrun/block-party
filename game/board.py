# Handles the playfield gameplay and HUD
from copy import copy

from game.playfield import PlayField, Step
from game.generator import Generator
from game import util
from game.grid import Grid


class GameInput:
    """Board input constant names."""

    @staticmethod
    def rotate_left() -> str:
        """Rotate to the left."""
        return "rotate_ccw"
    
    @staticmethod
    def rotate_right() -> str:
        """Rotate to the right."""
        return "rotate_cw"

    @staticmethod
    def left() -> str:
        """Move left."""
        return "left"

    @staticmethod
    def right() -> str:
        """Move right."""
        return "right"

    @staticmethod
    def soft_drop() -> str:
        """Fast drop."""
        return "soft_drop"
    
    @staticmethod
    def pause() -> str:
        """Pause gameplay."""
        return "pause"

    @staticmethod
    def resume() -> str:
        """Resume gameplay."""
        return GameInput.pause() # Toggle

    @staticmethod
    def hard_drop() -> str:
        """Hard drop."""
        return "hard_drop"

    @staticmethod
    def hold() -> str:
        """Hold piece."""
        return "hold"


class Board:
    """A Board is essentially a player's field and related game stats."""

    def __init__(self, width: int, height: int, block_data: dict,
        frames: list, name: str="player", init_level: int = 0):
        """
        width - Width of entire board.
        height - Height of entire board.
        frames - List of gravity frames for each level.
        name - Name of player.
        init_level - Initial level.
        """
        self._width = width
        self._height = height
        self._field = PlayField(block_data, "", init_level, frames)

        # Gameplay state
        self._fall_time = 0 # Timemes since last gravity effect
        self._clearing_time = 0 # Time so far animating line clear
        self._prev_pos = None # Last position placed
        self._score = 0
        self._name = name
        self._held = "" # Held block name
        self._hold_ready = True # Able to hold block at the moment?
        self.placed = False # Active block placed?
        self._lines = 0
        self._level = 0

        # Generator
        self._generator = Generator(list(block_data.keys()), 4)

        self.set_score(self._score)
        self.set_lines(0)
        self.set_name(self._name)
        self.set_level(0)

    def get_raw_grid(self) -> list:
        """Get the raw grid data, with ghost block."""
        return self._field.get_view().get_raw()

    def update(self, dt: float):
        # Line clear check/place check
        if self.placed:
            self._prev_pos = self._field.get_active_block()[0].get_position()
            filled = self._field.get_filled_rows()
            if len(filled) > 0:
                self._field.clear_filled_rows()
                # Adjust metrics
                self.set_score(self._score +
                    util.get_points(self._field.get_level(), len(filled)))
                self.set_lines(self._lines + len(filled))
                self.set_level(int(self._lines / 10))
            self._spawn_next()
            self._hold_ready = True

        self.placed = False

        if self._fall_time <= self._field.get_current_level_speed(dt):
            self._fall_time += dt
        else:
            self._fall_time = 0
            self.placed = self._field.step(Step.vertical())

    def has_lost(self) -> bool:
        """Check if current step has caused game over."""
        return self._prev_pos == self._field.get_spawn_position()

    def set_score(self, score: int):
        """Set current score."""
        self._score = score

    def set_name(self, name: str):
        """Set player name."""
        self._name = name

    def set_lines(self, count: int):
        """Set the lines cleared."""
        self._lines = count

    def set_level(self, n: int):
        """Set the current level."""
        self._level = n
        self._field.set_level(self._level)

    def _field_step(self, step: Step):
        """Perform a step."""
        self.placed = self._field.step(step)

    def performInput(self, inp: str):
        """Perform a game input command."""
        if inp == GameInput.left():
            self._field_step(Step.horizontal(True))
        elif inp == GameInput.right():
            self._field_step(Step.horizontal(False))
        elif inp == GameInput.soft_drop():
            self._field_step(Step.vertical())
        elif inp == GameInput.rotate_left():
            self._field_step(Step.rotate(1))
        elif inp == GameInput.rotate_right():
            self._field_step(Step.rotate(3))
        elif inp == GameInput.hard_drop():
            for r in range(self._field.get_height()):
                if not self._field.step(Step.vertical()):
                    continue
                self.placed = True
                break
        elif inp == GameInput.hold():
            if self._hold_ready:
                self._spawn_next(self._hold())
                self._hold_ready = False

    def _hold(self) -> str:
        """Swap the hold block name with the current block.
        If there is no block currently held: will return empty string.
        Otherwise, will swap and return the previously held block name.
        """
        if self._held == "":
            self._held = self._field.get_active_block()[1]
            return ""
        old_held = copy(self._held)
        self._held = self._field.get_active_block()[1]
        return old_held

    def _spawn_next(self, name: str = ""):
        """Spawn next generated block."""
        if name == "":
            front, mult = self._generator.pop_front()
            self._field.spawn(front, mult + 1)
        else:
            self._field.spawn(name)
