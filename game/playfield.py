from __future__ import annotations
from random import choice
import pygame
from pygame.locals import *

from game.grid import Grid


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


class ActiveBlock:
    """Basic active block data."""

    def __init__(self, x: int, y: int, data: list):
        self.reset(x, y, data)

    @classmethod
    def copy(cls, other: ActiveBlock):
        """Copy another ActiveBlock."""
        return cls(other.x, other.y, other._grid._grid)

    def reset(self, x: int, y: int, data: list):
        """Reset position and grid data."""
        self.x = x
        self.y = y
        self._grid = Grid.from_data(data)

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
                self._grid.rotate90(step.get_value())

    def get_grid(self) -> Grid:
        """Get the grid of the block."""
        return self._grid


class PlayField:
    """Handles the active block and its collisions."""

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
        self.spawn(initial_block)

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

    def get_spawn_position(self) -> tuple:
        """Get the coordinates of the spawn position."""
        return self._spawn_position

    def get_level_speed(self, level: int, dt: float = 1) -> int:
        """In frames."""
        return self._level_speeds[level] * dt

    def get_current_level_speed(self, dt: float = 1) -> int:
        """Current level speed in frames."""
        return self.get_level_speed(self.get_level(), dt)

    def _apply_multiplier(self, target: list, x: int) -> list:
        """Multiply all target values by x."""
        result = []
        for j in range(len(target)):
            result_row = []
            for i in range(len(target[j])):
                value = target[j][i]
                result_row.append(value * x)
            result.append(result_row)
        return result

    def spawn(self, i: str = "", multiplier: int = 1):
        """Spawn next block.
        Chooses random if i is empty string.
        Multiplies new active block grid values by multiplier.
        """
        block = self.get_random_block() if i == "" else self._blocks[i]
        self._active.reset(*self._spawn_position,
            self._apply_multiplier(block, multiplier))

    def get_block_data(self, name: str) -> list:
        """Get block grid data."""
        return self._blocks[name]

    def get_random_blockname(self) -> str:
        """Get random name of available blocks."""
        return choice(list(self._blocks.keys()))

    def get_random_block(self):
        """Get random block grid data."""
        return self.get_block_data(self.get_random_blockname())

    def get_view(self) -> Grid:
        """Get the merged grid of the field and active block."""
        mock = Grid.from_grid(self._field)
        x, y = self._active.get_position()
        mock.merge(self._active.get_grid(), x, y)
        return mock

    def _try_step(self, step: Step) -> ActiveBlock:
        """Attempt a given Step.
        Return a new ActiveBlock if no conflicts
        occur from the step; otherwise None is returned.
        """
        if step is not None:
            active_copy = ActiveBlock.copy(self._active)
            active_copy.perform_step(step)
            if not self._field.has_conflict(active_copy.get_grid(),
                active_copy.x, active_copy.y):
                return active_copy
        else:
            raise ValueError("Cannot try step if None")
        return None

    def step(self, step: Step) -> bool:
        """Request to perform a Step.
        Returns True if block was placed.
        """
        result = self._try_step(step)
        if result is not None:
            self._active = result
        else: # Returned None; invalid step
            # Vertical conflict means time to place in field
            if step.get_type() == "vertical":
                active_pos = self._active.get_position()
                self._field.merge(self._active.get_grid(),
                    *active_pos)
                self._filled_rows = self._field.get_filled_rows(0,
                    self.get_height())
                return True
        return False

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
