# Handles the playfield gameplay and HUD
import pygame
from pygame.locals import *

from game.playfield import PlayField, Step, ActiveBlock
from game.component import Text, HUDDisplay
from game.grid import Renderers, BasicGridRenderer


class GameInput:
    """Basic set of possible inputs for the board."""

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


class Board(pygame.sprite.LayeredDirty):
    """Handler for playfield and related HUD."""

    def __init__(self, width: int,
        height: int, configuration: dict, block_data: dict, block_cols: list,
        frames: list, font: pygame.font.Font,
        background: pygame.Surface, play_background: pygame.Surface,
        init_level: int = 0):
        """
        width - Width of entire board.
        height - Height of entire board.
        configuration - "board" configuration data.
        block_data - Dictionary of blocks and their raw grids.
        block_cols - List of block colors (RGB lists).
        frames - List of gravity frames for each level.
        font - Font to render.
        background - Background of board.
        play_background - Background of play field.
        init_level - Initial level.
        """
        super().__init__()
        self._width = width
        self._height = height
        self._font = font
        self._bg = background
        self._fg = play_background
        self._field = PlayField(block_data, "", init_level, frames)

        # Gameplay state
        self._fall_time = 0 # Frames since last gravity effect
        self._clearing = False # Currently clearing animation?
        self._next_block = self.force_next("") # Next block (ActiveBlock)
        self._prev_pos = None # Last position placed

        # HUD displays
        self._displays = {}
        self._bdisplay = None # Background display for HUD displays
        self._setup(configuration)

        # Renderers
        self._renderer = Renderers([BasicGridRenderer(block_cols)])

        self._field.step(Step.vertical())

    def update(self, dt: float):
        self._renderer.update(self._field.get_view(), dt)
        dest = pygame.Surface((self._width, self._height))  # Pay attention to dimensions...
        self._renderer.render(self._field.get_view(), dest)
        self.update_board("playfield", dest)

    def force_next(self, block: str) -> ActiveBlock:
        """Force what the next block will be.
        Empty string for random.
        """
        if block == "":
            self._next_block = self._field.get_random_block()
        else:
            self._next_block = self._field.get_block_data(block)
        return self._next_block

    def has_lost(self) -> bool:
        """Check if current step has caused game over.
        """
        return self._prev_pos == self._field.get_spawn_position()

    def set_score(self, score: int):
        """Set current score."""
        self._score = abs(score)
        self.update_board("points", Text(""))

    def performInput(self, inp: str):
        """Perform a game input command."""
        if inp == GameInput.left():
            self._field.step(Step.horizontal(True))
        elif inp == GameInput.right():
            self._field.step(Step.horizontal(False))
        elif inp == GameInput.soft_drop():
            self._field.step(Step.vertical())
        elif inp == GameInput.rotate_left():
            self._field.step(Step.rotate(1))
        elif inp == GameInput.rotate_right():
            self._field.step(Step.rotate(3))
        elif inp == GameInput.hard_drop():
            pass  # TODO

    def _setup(self, config: dict):
        self._bdisplay = pygame.image.load(config["boardBackground"])
        layout = config["layout"]
        for name, data in layout.items():
            # Required parameters:
            position = data["position"] # Raw position values
            title = str(data["title"])
            # Calculated position and dimensions
            point = (position[0] * self._width, position[1] * self._height)
            dimensions = (position[2] * self._width, position[3] * self._height)

            # Interval is non-zero if it is for the statistic display
            interval = 0
            if "interval" in data:
                interval = data["interval"]

            self._displays[name] = HUDDisplay(point[0], point[1],
                dimensions[0], dimensions[1],
                self._bdisplay, None,
                title,
                self._font)
            self.add(self._displays[name])

    def update_board(self, name: str, content: pygame.Surface):
        """Update content Surface of a HUD board."""
        if name in self._displays:
            self._displays[name].update_content(content)
