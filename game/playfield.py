from __future__ import annotations
from random import choice

from game.grid import Grid


class Step:
    """
    A request to modify the active block in the playfield.
    """

    def __init__(self, step_type: str, value: int = 1):
        self._type = step_type
        self._value = value

    @classmethod
    def horizontal(cls, left: bool):
        """
        left - Set to True if left movement.
        """
        return cls("horizontal", -1 if left else 1)

    @classmethod
    def vertical(cls):
        return cls("vertical")

    @classmethod
    def rotate(cls, right_turns: int = 1):
        return cls("rotate", right_turns)

    def get_type(self) -> str:
        return self._type

    def get_value(self) -> int:
        return self._value


class ActiveBlock:
    """
    Basic active block data.
    """

    def __init__(self, x: int, y: int, data: list):
        self.x = x
        self.y = y
        self._grid = Grid.from_data(data)

    @classmethod
    def copy(cls, other: ActiveBlock):
        return cls(other.x, other.y, other._grid._grid)

    def get_position(self) -> tuple:
        return self.x, self.y

    def perform_step(self, step: Step):
        if step is not None:
            s_type = step.get_type()
            if s_type == "horizontal":
                self.x += step.get_value()
            elif s_type == "vertical":
                self.y += step.get_value()
            elif s_type == "rotate":
                self._grid.rotate90(step.get_value())

    def get_grid(self) -> Grid:
        return self._grid


class PlayField:
    """
    Handles the active block and its collisions.
    """

    def __init__(self, block_data: dict, initial_block: str,
        initial_level: int = 0, level_speeds: list = [53],
        spawn_position: tuple = None):
        """
        block_data - Block grids.
        initial_block - Initial block to spawn.
        initial_level - Initial starting level. Must be valid index.
        level_speeds - Level gravity info (frames per row).
        spawn_position - Active spawn position. None for default.
        """
        self._blocks = block_data
        if len(block_data) < 1 or block_data is None:
            raise ValueError("block_data must be valid")
        self._field = Grid.create_default()
        self._level = initial_level
        self._level_speeds = level_speeds
        if spawn_position is not None:
            self._spawn_position = spawn_position
        else:
            self._spawn_position = self.get_width() // 2, 0
        # Active block
        self._active = ActiveBlock(*self._spawn_position,
            block_data[initial_block])

    def get_level(self) -> int:
        return self._level

    def set_level(self, l: int):
        if l <= 0:
            self._level = 0
        elif l >= len(self._level_speeds):
            self._level = len(self._level_speeds)
        else:
            self._level = l

    def get_level_speed(self, level: int, dt: float = 1) -> int:
        """
        In frames.
        """
        return self._level_speeds[level] * dt

    def spawn(self, i: int = -1):
        """
        Spawn next block. Chooses random if i < 0.
        """
        block = self._get_random_block() if i < 0 else list(self._blocks)[i]
        self._active = ActiveBlock(*self._spawn_position, block)

    def _get_random_block(self):
        result = choice(list(self._blocks.keys()))
        return self._blocks[result]

    def get_view(self) -> Grid:
        """
        Get the merged grid of the field and active block.
        """
        mock = Grid.from_grid(self._field)
        x, y = self._active.get_position()
        mock.merge(self._active.get_grid(), x, y)
        return mock

    def _try_step(self, step: Step) -> ActiveBlock:
        """
        Attempt a given Step. Return a new ActiveBlock if no conflicts
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
        """
        Attempt a given Step. Returns True if successful and updates
        the active block. False if cannot perform movement, and if
        step type is "vertical", will automatically merge to playfield
        and spawn new block.
        """
        result = self._try_step(step)
        if result is not None:
            self._active = result
            return True
        else:
            # Vertical conflict means time to place in field
            if step.get_type() == "vertical":
                self._field.merge(self._active.get_grid(),
                    *self._active.get_position())
                self.spawn()
        return False

    def get_width(self):
        return self._field.get_width()

    def get_height(self):
        return self._field.get_height()
