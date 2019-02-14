from __future__ import annotations

class Grid:

    def __init__(self, rows: int, cols: int, fill: int = 0):
        """
        rows - Height.
        cols - Width.
        fill - Fill value for each position.
        """
        # 2D list
        if rows <= 0 or cols <= 0:
            raise ValueError("Grid dimensions should be > 0")
        self._grid = [[fill for _ in range(cols)] for __ in range(rows)]
    
    @classmethod
    def create_default(cls):
        """
        Create a standard tetris board instance.
        """
        return cls(20, 10)

    @classmethod
    def from_data(cls, data: list):
        """
        Create a grid from given 2D list.
        """
        if len(data) < 1:
            raise ValueError("'data' rows must be length >= 1")
        elif len(data[0]) < 1:
            raise ValueError("'data' columns must be length >= 1")
        else:
            result = cls(len(data), len(data[0]))
            for j in range(len(data)):
                result._grid[j] = data[j][:]
            return result

    @classmethod
    def from_grid(cls, grid: Grid):
        return Grid.from_data(grid._grid)

    def __eq__(self, other: Grid):
        return self._grid == other._grid

    def __str__(self):
        return "w: {} x h: {} :: {}" \
            .format(*self.get_dimensions(), str(self._grid))

    def set_at(self, x: int, y: int, value: int = 0):
        self._grid[y][x] = value

    def get_height(self):
        return len(self._grid)

    def get_width(self):
        return len(self._grid[0])

    def get_row(self, i):
        return self._grid[i]

    def get_at(self, x: int, y: int):
        return self._grid[y][x]

    def get_dimensions(self) -> tuple:
        """
        Get the width, height of the grid.
        """
        return self.get_width(), self.get_height()

    def merge(self, grid: Grid, x: int = 0, y: int = 0,
        transparent: bool = True):
        """
        Merge a grid. Will not overwrite non-zero values if a zero in the grid
        is in its place, unless transparent is set to False.
        """
        if grid is None:
            raise ValueError("Cannot merge with None")
        
        w = grid.get_width()
        h = grid.get_height()
        x = abs(x)
        y = abs(y)
        if self.can_fit(grid, x, y):
            # Copy subgrid into parent grid
            for i, row in zip(range(h), grid._grid):
                for j, value in zip(range(w), grid.get_row(i)):
                    # Don't overwrite non-0 from subgrid if subgrid val is 0
                    if transparent and value == 0:
                        continue
                    self._grid[y + i][x + j] = value
        else:
            raise ValueError(("Subgrid (w {w}, h {h}) cannot fit into parent grid" +
                " at point (x {x}, y {y})").format(w=w, h=h, x=x, y=y))

    def can_fit(self, grid: Grid, x: int = 0, y: int = 0) -> bool:
        """
        Check if given grid can fit/merge.
        """
        if grid is None:
            return False
        w = self.get_width()
        h = self.get_height()
        #in_bounds = x >= 0 and x < w and y >= 0 and y < h
        in_bounds = self.point_within(x, y)
        x_max = x + grid.get_width() <= w
        y_max = y + grid.get_height() <= h
        return in_bounds and x_max and y_max

    def point_within(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.get_width() and \
            y >= 0 and y < self.get_height()

    def has_conflict(self, grid: Grid, x: int = 0, y: int = 0):
        """
        Check for merge conflict between grids. A merge conflict
        is when the two grids both have non-zero values that overlap
        positions. However, a zero in the given grid is not
        conflicting if the parent grid has a non-zero in the same
        position. A grid that ends up being out of bounds or too
        large to merge is also considered conflicting.
        """
        if self.can_fit(grid, x, y):
            o_width = grid.get_width()
            o_height = grid.get_height()
            for oj, j in zip(range(o_height), range(y, o_height + y)):
                for oi, i in zip(range(o_width), range(x, o_width + x)):
                    o = grid.get_at(oi, oj)
                    base = self.get_at(i, j)
                    if base != 0 and o != 0:
                        return True
        else:
            return True
        return False

    def rotate90(self, n: int = 1):
        """
        Rotate 90 degrees clockwise, n amount of times.
        """
        for _ in range(abs(n)):
            dim = self.get_dimensions()
            result = Grid(dim[0], dim[1])
            colIndex = result.get_width()
            for j in range(self.get_height()):
                colIndex -= 1
                for i in range(self.get_width()):
                    result.set_at(colIndex, i, self.get_at(i, j))
            self._grid = result._grid

    def set_row(self, y: int, data: list):
        """
        Set row data. Must be same length as width.
        """
        data_len = len(data)
        if data_len != self.get_width():
            raise ValueError(
                "Cannot set row with data of length {}".format(data_len))
        elif not self.point_within(0, y):
            raise ValueError("Cannot set row at invalid y: {}".format(y))
        else:
            self._grid[y] = data

    def shift_row(self, y: int, yf: int):
        """
        Shift row y to row yf, fills row y with zeros.
        """
        if self.point_within(0, y) and self.point_within(0, yf):
            self.set_row(yf, self.get_row(y))
            self.set_row(y, [0 for _ in range(self.get_width())])
        else:
            raise ValueError("Cannot shift row from {} to {}".format(y, yf))

    def shift_rows(self, y0: int, y1, step: int):
        """
        Shift rows y0 to y1 (inclusive) by step. Positive step
        means moving "down the grid," or Y index increases.
        """
        selection = self.get_rows(y0, y1)
        sel_height = len(selection)
        # If step is positive, we need to iterate bottom-up
        # Otherwise, we iterate top-down
        for y in self._shift_row_values(step, y0, sel_height):
            self.shift_row(y, y + step)

    def _shift_row_values(self, step: int, y0: int, height: int):
        """
        Get the indexes of the rows that are to be shifted.
        """
        if step >= 0:
            return range(y0 + height - 1, y0 - 1, -1)
        else:
            return range(y0, y0 + height)

    def get_rows(self, y0: int, y1: int) -> list:
        """
        Get a copy of the rows from y0 to y1 (inclusive). None is returned
        if invalid rows are given.
        """
        if self.point_within(0, y0) and self.point_within(0, y1) and y1 >= y0:
            return self._grid[y0:y1 + 1]
        else:
            return None

    def row_is_zero(self, y: int) -> bool:
        """
        Test if row is filled with zeros.
        """
        return [0 for _ in range(self.get_width())] == self.get_row(y)

    def row_is_filled(self, y: int) -> bool:
        """
        Test if row is filled with non-zero values.
        """
        if not self.point_within(0, y):
            raise ValueError("Cannot test invalid row {}".format(y))
        for value in self.get_row(y):
            if value == 0:
                return False
        return True

    def fill_row(self, r: int, value: int):
        """
        Fill row r with value.
        """
        self.set_row(r, [value for _ in range(self.get_width())])

    def get_filled_rows(self, y0: int, y1: int) -> list:
        filled = []
        for j in range(y1 - y0):
            if self.row_is_filled(y0 + j):
                filled.append(j)
        return filled
