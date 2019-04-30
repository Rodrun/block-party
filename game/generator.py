import random


class Generator:
    """Generator for systematically random block stack.
    This somewhat helps prevents floods and I-piece droughts. Modeled after
    the Tetris "7-bag" randomizer.
    """

    def __init__(self, names: list, preview_size: int = 4, seed = None,
            bag_size: int = 7):
        """
        names - List of block name strings.
        preview_size - Length of future block preview. Used to determine when
            to make new bags.
        seed - Random generator seed.
        """
        random.seed(seed)
        self._names = names
        self._preview_size = preview_size
        self._bag_size = len(names)
        self.stack = []
        self._fill_stack()

    @property
    def preview_size(self) -> int:
        return self._preview_size

    @preview_size.setter
    def preview_size(self, n: int):
        if n < 1:
            raise ValueError("preview_size must be > 0")
        else:
            self._preview_size = n

    @property
    def bag_size(self) -> int:
        return self._bag_size

    @bag_size.setter
    def bag_size(self, n: int):
        raise Error("bag_size should not be changed")

    @property
    def names(self) -> list:
        return self._names

    @names.setter
    def names(self, h: list):
        if isinstance(h, list):
            self._names = h
        else:
            raise TypeError("names must be instace of list")

    def pop_front(self) -> tuple:
        """Pop the front of the stack and return it.
        Returns the string name of the font and its integer equivalent."""
        front = self.stack.pop(0)
        popped = self.names[front]
        self._fill_stack()
        return popped, front

    def get_front(self) -> tuple:
        """Get the front of the list, but do not pop."""
        return self.names[self.stack[0]], self.stack[0]

    def _fill_stack(self):
        """Fill the stack so it contains > preview_size elements."""
        while len(self.stack) <= self._preview_size:
            self.stack.extend(self.make_bag())

    def make_bag(self) -> list:
        """Make a bag of size len(names)"""
        bag = []
        free = [x for x in range(self.bag_size)]
        for i in range(len(free)):
            select = random.choice(free)
            bag.append(select)
            free.remove(select)
        return bag
