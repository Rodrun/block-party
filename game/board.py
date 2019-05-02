# Handles the playfield gameplay and HUD
from copy import copy

import pygame
from pygame.locals import *

from game.playfield import PlayField, Step
from game.component import Text, HUDDisplay, render_text
from game.generator import Generator
from game.renderer import BasicGridRenderer, get_cell_dim
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


class Board(pygame.sprite.LayeredDirty):
    """Handler for playfield and related HUD."""

    def __init__(self, width: int,
        height: int, configuration: dict, block_data: dict, block_cols: list,
        frames: list, font: pygame.font.Font, name: str,
        background: pygame.Surface = None,
        play_background: pygame.Surface = None,
        init_level: int = 0):
        """
        width - Width of entire board.
        height - Height of entire board.
        configuration - "board" configuration data.
        block_data - Dictionary of blocks and their raw grids.
        block_cols - List of block colors (RGB lists).
        frames - List of gravity frames for each level.
        font - Font to render.
        name - Name of player.
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

        # HUD displays
        self._displays = {}
        self._bdisplay = None # Background for HUD displays
        self._setup(configuration)

        # Renderers
        self._renderer = BasicGridRenderer(block_cols, self._field.get_grid())
        self._hold_rend = BasicGridRenderer(block_cols, Grid(4, 4))
        self._next_rend = BasicGridRenderer(block_cols, Grid(4, 4))

        self.set_score(self._score)
        self.set_lines(0)
        self.set_name(self._name)
        self.set_level(0)

    def update(self, dt: float):
        # HUD
        self._renderer.grid = self._field.get_view()
        self._renderer.update(dt)
        dest = pygame.Surface((self._width, self._height))  # Pay attention to dimensions...
        self._renderer.render(dest)
        self.update_board("playfield", dest)

        cell_dim = get_cell_dim(self._field.get_view(),
            self._displays["playfield"].content)

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
        self._score = abs(score)
        self.update_board("points",
            render_text(util.format_int(self._score), self._font))

    def set_name(self, name: str):
        """Set player name."""
        self._name = name
        self.update_board("name", render_text(self._name, self._font))

    def set_lines(self, count: int):
        """Set the lines cleared."""
        self._lines = count
        self.update_board("lines", render_text(str(self._lines), self._font))

    def set_level(self, n: int):
        """Set the current level."""
        self._level = n
        self._field.set_level(self._level)
        self.update_board("level", render_text(str(self._level), self._font))

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
            self.redraw_hold()
            return ""
        old_held = copy(self._held)
        self._held = self._field.get_active_block()[1]
        self.redraw_hold()
        return old_held

    def redraw_hold(self):
        """Redraw the hold block board."""
        dest = pygame.Surface((250, 250))
        self._hold_rend.grid = self._field.get_block(self._held).get_grid()
        self._hold_rend.render(dest)
        self.update_board("hold", dest)

    def _spawn_next(self, name: str = ""):
        """Spawn next generated block."""
        if name == "":
            front, mult = self._generator.pop_front()
            self._field.spawn(front, mult + 1)
        else:
            self._field.spawn(name)
        self.redraw_next()

    def _setup(self, config: dict):
        try:
            self._bdisplay = pygame.image.load(config["boardBackground"])
        except:
            print("Note: _bdisplay is None (no display board bg)")

        layout = config["layout"]
        for name, data in layout.items():
            # Required parameters:
            position = data["position"] # Raw position values
            title = str(data["title"])
            # Optional parameters
            proportion = True
            if "proportion" in data:
                proportion = data["proportion"]
            # Calculated position and dimensions
            point = (position[0] * self._width, position[1] * self._height)
            dimensions = (position[2] * self._width, position[3] * self._height)

            testSurf = pygame.Surface((1, 1), pygame.SRCALPHA)
            testSurf.convert_alpha()
            self._displays[name] = HUDDisplay(point[0], point[1],
                dimensions[0], dimensions[1],
                self._bdisplay, testSurf,
                title,
                self._font,
                proportion=proportion)
            self.add(self._displays[name])

    def update_board(self, name: str, content: pygame.Surface):
        """Update content Surface of a HUD board."""
        if name in self._displays:
            self._displays[name].update_content(content)

    def redraw_next(self):
        """Update the Next block preview board."""
        dest = pygame.Surface((250, 250))
        name, mul = self._generator.get_front()
        self._next_rend.grid = self._field.get_block(name).get_grid()
        self._next_rend.grid.apply_multiplier(mul + 1)
        self._next_rend.render(dest)
        self.update_board("next", dest)
