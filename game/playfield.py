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

class PlayField:
    """
    Handles the active block and its collisions.
    """

    def __init__(self, block_data: dict, initial_block: int = 0):
        """
        """
        self._blocks = block_data
        if len(block_data) < 1 or block_data is None:
            raise ValueError("block_data must be valid")
        self._field = Grid.create_default()
        self._tick = 0

    def update(self):
        pass

    def set_next(self, name: str):
        """
        Set next block.
        """
        pass

    def _get_block_i(self, i: int) -> list:
        """
        Get block data from index.
        """
        return list(self._blocks)[i]

    def get_field(self):
        return self._field

    def try_step(self, step: Step) -> bool:
        pass

    def get_width():
        return self._field.get_width()

    def get_height():
        return self._field.get_height()
