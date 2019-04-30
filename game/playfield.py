from __future__ import annotations
from random import choice
import pygame
from pygame.locals import *

from game.grid import Grid
from game import util


class Step:
    """A request to modify the active block in the playfield."""

    def __init__(self, step_type: str, value: int = 1):
        self._type = step_type
        self._value = value

    @classmethod
    def horizontal(cls, left: bool):
        """Horizontal step.

        left - Set to True if left movement.
        """
        return cls("horizontal", -1 if left else 1)

    @classmethod
    def vertical(cls):
        """Vertical (soft drop) step."""
        return cls("vertical")

    @classmethod
    def rotate(cls, right_turns: int = 1):
        """Rotation step."""
        return cls("rotate", right_turns)

    def get_type(self) -> str:
        """Get type of step."""
        return self._type

    def get_value(self) -> int:
        """Get value of step."""
        return self._value

    def is_rotate(self) -> bool:
        """Is this step a rotation step?"""
        return self._type == "rotate"


class ActiveBlock:
    """Basic active block data.
    An active block is one that isn't placed on the field (yet)."""

    def __init__(self, x: int, y: int, data: list, ghost: bool = False,
        rotations: int = 0, name=""):
        self.reset(x, y, data, ghost, rotations, name)

    @classmethod
    def copy(cls, other: ActiveBlock, ghost: bool = False):
        """Copy another ActiveBlock."""
        return cls(other.x, other.y, other._grid._grid[:], ghost,
            other.rotations, other.name)

    def reset(self, x: int, y: int, data: list, ghost: bool = False,
        rot: int = 0, name: str = ""):
        """Reset position and grid data."""
        self.x = x
        self.y = y
        real_data = data[:] if not ghost else util.apply_multiplier(data, -1)
        self._grid = Grid.from_data(real_data)
        self.rotations = rot # Rotations from spawn rotation
        self.name = name

    def get_position(self) -> tuple:
        """Get the current position on the field."""
        return self.x, self.y

    def perform_step(self, step: Step):
        """Perform step to ActiveBlock."""
        if step is not None:
            s_type = step.get_type()
            if s_type == "horizontal":
                self.x += step.get_value()
            elif s_type == "vertical":
                self.y += step.get_value()
            elif s_type == "rotate":
                # Warn: Assumes only 1 or 3 rotations is passed in as value!
                self.rotations += 1 if step.get_value() == 1 else -1
                if self.rotations < 0:
                    self.rotations = 3
                elif self.rotations > 3:
                    self.rotations = 0
                self._grid.rotate90(step.get_value())

    def get_grid(self) -> Grid:
        """Get the grid of the block."""
        return self._grid

    def __str__(self) -> str:
        return str(self._grid)


class PlayField:
    """Handles the active block and its collisions."""

    # Wall kick coordinate pairs, Y is inverted
    _KICK = {
        # TTC's SRS variation
        "0": [(0, 0)],
        "1": [(1, 0), (1, -1), (0, 2), (1, 2)],
        "2": [(0, 0)],
        "3": [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        # O block
        "0O": [(0, 0)],
        "1O": [(0, -1)],
        "2O": [(-1, -1)],
        "3O": [(-1, 0)],
        # I block
        "0I": [(-1, 0), (2, 0), (-1, 0), (2, 0)],
        "1I": [(-1, 0), (0, 1), (0, -2)],
        "2I": [(-1, 1), (1, 1), (-2, 1), (1, 0), (-2, 0)],
        "3I": [(0, 1), (0, 1), (0, 1), (0, -1), (0, 2)]
    }

    def __init__(self, block_data: dict, initial_block: str,
        initial_level: int = 0, level_speeds: list = [53],
        spawn_position: tuple = None, dimensions: tuple =None):
        """
        block_data - Block grids.
        initial_block - Initial block to spawn.
        initial_level - Initial starting level. Must be valid index.
        level_speeds - Level gravity info (frames per row).
        spawn_position - Active spawn position. None for default.
        dimensions - Set to None for default board dimensions (row, col).
        """
        self._blocks = block_data
        if len(block_data) < 1 or block_data is None:
            raise ValueError("block_data must be valid")

        if dimensions is not None:
            self._field = Grid.create_default(*dimensions)
        else:
            self._field = Grid.create_default()

        self._level = initial_level
        self._level_speeds = level_speeds
        self._filled_rows = []
        if spawn_position is not None:
            self._spawn_position = spawn_position
        else:
            self._spawn_position = self.get_width() // 2, 0

        # Active block
        self._active = ActiveBlock(*self._spawn_position,
            [[0]])
        self._active_name = ""  # Name of active block
        self.spawn(initial_block)

    def get_grid(self) -> Grid:
        return self._field

    def get_level(self) -> int:
        """Get current level."""
        return self._level

    def set_level(self, l: int):
        """Set the current level."""
        if l <= 0:
            self._level = 0
        elif l >= len(self._level_speeds):
            self._level = len(self._level_speeds)
        else:
            self._level = l

    def get_active_block(self) -> tuple:
        """Get the current active block and name."""
        return self._active, self._active_name

    def get_spawn_position(self) -> tuple:
        """Get the coordinates of the spawn position."""
        return self._spawn_position

    def get_level_speed(self, level: int, dt: float = 1) -> int:
        """In frames."""
        return self._level_speeds[level] * dt

    def get_current_level_speed(self, dt: float = 1) -> int:
        """Current level speed in frames."""
        return self.get_level_speed(self.get_level(), dt)

    def spawn(self, i: str = "", multiplier: int = 1):
        """Spawn next block.
        Chooses random if i is empty string.
        Multiplies new active block grid values by multiplier.
        """
        try:
            if i == "":
                block, nm = self.get_random_block()
            else:
                block, nm = self._blocks[i], i
            self._active.reset(*self._spawn_position,
                util.apply_multiplier(block, multiplier),
                name=nm)
            self._active_name = nm
        except(KeyError):
            print("Warning: tried to spawn invalid block '{}'".format(i))

    def get_block_data(self, name: str) -> list:
        """Get block grid data."""
        return self._blocks[name]

    def get_block(self, name: str) -> ActiveBlock:
        """Get block as an ActiveBlock object."""
        return ActiveBlock(0, 0, self.get_block_data(name))

    def get_random_blockname(self) -> str:
        """Get random name of available blocks."""
        return choice(list(self._blocks.keys()))

    def get_random_block(self):
        """Get random block grid data.
        Returns grid of selected block and string name of it.
        """
        name = self.get_random_blockname()
        return self.get_block_data(name), name

    def get_view(self, ghost: bool = True) -> Grid:
        """Get the merged grid of the field and active block."""
        mock = Grid.from_grid(self._field)
        # Ghost block
        if ghost:
            g_block = self.get_ghost_block()
            mock.merge(g_block.get_grid(), *g_block.get_position())
        # Active block
        mock.merge(self._active.get_grid(), *self._active.get_position())
        return mock

    def try_step_with(self, ab: ActiveBlock, step: Step) -> ActiveBlock:
        """Attempt a given step with a given active block.
        Return a new ActiveBlock if no conflicts; None otherwise.
        """
        if step is not None:
            active_copy = ActiveBlock.copy(ab)
            o_rotation = active_copy.rotations # Old rotations value
            active_copy.perform_step(step)

            if not self._field.has_conflict(active_copy.get_grid(),
                active_copy.x, active_copy.y):
                return active_copy
            elif step.is_rotate():
                # Store original coordinates
                o_x, o_y = active_copy.get_position()
                key = str(active_copy.rotations)
                if ab.name == "O" or ab.name == "I":
                    key += ab.name
                tests = PlayField._KICK[key]
                for kick in tests:
                    active_copy.x += kick[0]
                    active_copy.y -= kick[1] # Inverted Y

                    conf = self._field.has_conflict(active_copy.get_grid(),
                        active_copy.x, active_copy.y)
                    if conf:
                        active_copy.x = o_x
                        active_copy.y = o_y
                    else:
                        return active_copy
        return None

    def try_step(self, step: Step) -> ActiveBlock:
        """Attempt a given Step with current active block.
        Return a new ActiveBlock if no conflicts
        occur from the step; otherwise None is returned.
        """
        return self.try_step_with(self._active, step)

    def step(self, step: Step) -> bool:
        """Request to perform a Step.
        Returns True if block was placed.
        """
        result = self.try_step(step)
        if result is not None:
            self._active = result
        else: # Returned None; invalid step
            # Vertical conflict means time to place in field
            if step.get_type() == "vertical":
                active_pos = self._active.get_position()
                self._field.merge(self._active.get_grid(),
                    *active_pos)
                active_row = active_pos[1]
                remaining = self._get_remaining_rows(active_row)
                self._filled_rows = self._field.get_filled_rows(active_row,
                    active_row + remaining)
                return True
        return False

    def _get_remaining_rows(self, row: int):
        """Get remaining rows left from bottom, in respect to given row."""
        bottom = self.get_height()
        diff = bottom - row
        if diff <= 0:
            return 0
        return diff

    def get_filled_rows(self) -> list:
        """Get list of non-zero filled rows."""
        return self._filled_rows

    def clear_filled_rows(self):
        """Clear all non-zero filled rows."""
        for y in self.get_filled_rows():
            self._field.shift_rows(0, y - 1, 1)
        self._filled_rows = []

    def get_width(self) -> int:
        """Get grid width."""
        return self._field.get_width()

    def get_height(self) -> int:
        """Get grid height."""
        return self._field.get_height()

    def get_ghost_block(self) -> ActiveBlock:
        """Get the 'ghost' block from the active block.
        Ghost blocks should have negative values.
        """
        ghost = ActiveBlock.copy(self._active, False)
        for r in range(self.get_height()):
            if self.try_step_with(ghost, Step.vertical()) is not None:
                ghost.y += 1
                continue
            break
        ghost._grid.apply_multiplier(-1)
        return ghost
