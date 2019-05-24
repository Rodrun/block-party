from __future__ import annotations

from game import util


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

    def get_height(self) -> int:
        return len(self._grid)

    def get_width(self) -> int:
        if self.get_height() < 1:
            return 0
        return len(self._grid[0])

    def get_row(self, i: int) -> list:
        if self.get_height() < 1:
            return []
        return self._grid[i][:]

    def get_col(self, x: int) -> list:
        return [self.get_at(x, i) for i in range(self.get_height())]

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

        fits, target, pos = self.can_fit(grid, x, y)
        w = target.get_width()
        h = target.get_height()
        x, y = pos
        if fits:
            # Copy subgrid into parent grid
            for i in range(h):
                for j, value in zip(range(w), target.get_row(i)):
                    # Don't overwrite non-0 from subgrid if subgrid val is 0
                    if transparent and value == 0:
                        continue
                    self._grid[y + i][x + j] = value
        else:
            raise ValueError(("Subgrid (w {w}, h {h}) cannot fit into parent grid" +
                " at point (x {x}, y {y})").format(w=w, h=h, x=x, y=y))

    def can_fit(self, grid: Grid, x: int = 0, y: int = 0) -> tuple:
        """
        Check if given grid can fit/merge.
        Returns boolean if can, a trimmed grid (or just the original
        grid that was passed in, if no trimming necessary), and
        offset coordinate pair (tuple) from trimming.
        """
        if grid is None:
            return False
        w = self.get_width()
        h = self.get_height()
        trimmed = Grid.from_grid(grid)
        xo, yo = trimmed.trim()
        x += xo
        y += yo
        in_bounds = self.point_within(x, y)
        x_max = x + trimmed.get_width() <= w
        y_max = y + trimmed.get_height() <= h
        return in_bounds and x_max and y_max, trimmed, (x, y)

    def trim(self) -> tuple:
        """Remove all empty rows and columns at edges.
        Returns X and Y offsets from the top left corner. For example, in
        a 3x3 grid: if row 0 and column 0 are trimmmed, the x and y offsets
        would be 1, 1. If row 2 was trimmed, and col 2 was trimmed, the
        x and y offsets would be 0, 0 -- because trimming those rows and
        columns did not affect the origin.
        """
        orig_w, orig_h = self.get_dimensions()
        xoff, yoff = 0, 0
        # Iterate through the rows and add only the rows that arent 0s
        # Do it again, but for the columns
        # It may reduce the ability to make spaces between blocks,
        # But right now it doesn't matter

        # Non zero rows
        top = []
        hit_edge = False
        for r in range(self.get_height()):
            if not self.row_is_zero(r):
                top.append(self.get_row(r))
                hit_edge = True
            if not hit_edge:
                yoff += 1
        self._grid = top
        
        # Non zero cols
        left = []
        hit_edge = False
        for c in range(self.get_width()):
            if not self.col_is_zero(c):
                left.append(self.get_col(c))
                hit_edge = True
            if not hit_edge:
                xoff += 1
        self._grid = Grid.col_to_rows(left)

        if self.get_height() < 1:
            xoff, yoff = 0, 0
        return xoff, yoff

    @staticmethod
    def col_to_rows(cols: list):
        """Convert columns to rows.
        Assumes that all columns are the same length.
        """
        if len(cols) < 1:
            return []
        rows = [[] for _ in cols[0]]
        for column in cols:
            r_index = 0
            for val in column:
                rows[r_index].append(val)
                r_index += 1
        return rows

    def get_nonzero_cols(self, x0: int, x1: int = -1):
        """Get the non zero-filled columns from [x0, x1).
        x0 - Initial column index.
        x1 - Final (exclusive) column index. -1 for end.
        Returns a generator.
        """
        if x1 < 0:
            x1 = self.get_width()
        for x in range(x0, x1):
            if not self.col_is_zero(x):
                yield self.get_col(x)

    def get_nonzero_rows(self, y0: int, y1: int = -1):
        """Get the non zero-filled rows from [y0, y1).
        y0 - Initial row index.
        y1 - Final (exclusive) row index. -1 for end.
        Returns a generator.
        """
        if y1 < 0:
            y1 = self.get_height()
        for y in range(y0, y1):
            if not self.row_is_zero(y):
                yield self.get_row(y)

    def remove(self, row: bool, value: int):
        """Remove a row or column (if row is False)."""
        if row:
            self._grid.pop(value)
        else:
            for y in range(self.get_height()):
                row = self.get_row(y)
                row.pop(value)
                # Not using set_row as it enforces width
                self._grid[y] = row[:]

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
        fits, target, pos = self.can_fit(grid, x, y)
        x, y = pos
        if fits:
            o_width = target.get_width()
            o_height = target.get_height()
            for oj, j in zip(range(o_height), range(pos[1], o_height + y)):
                for oi, i in zip(range(o_width), range(pos[0], o_width + x)):
                    o = target.get_at(oi, oj)
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

    def get_cols(self, x0: int, x1: int) -> list:
        """Get a copy of the columns from y0 to y1 (inclusive)."""
        if self.point_within(0, x0) and self.point_within(0, x1) and x1 >= x0:
            return [self.get_col(x) for x in range(x0, x1 + 1)]
        else:
            return None

    def row_is_zero(self, y: int) -> bool:
        """Test if row is filled with zeros."""
        return [0] * self.get_width()  == self.get_row(y)

    def col_is_zero(self, x: int) -> bool:
        """Test if column is filled with zeros."""
        return self.col_is_filled(x, 0)

    def col_is_filled(self, x: int, value) -> bool:
        """Test if column is filled with value."""
        return [value] * self.get_height() == self.get_col(x)

    def row_is_filled(self, y: int) -> bool:
        """
        Test if row is filled with non-zero values.
        """
        if self.get_height() < 1:
            return False
        elif not self.point_within(0, y):
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
        """Get a list of row indexes that are filled within [y0, y1) range.
        ValueError will be raised if y0 > y1, or 0 <= (y0 or y1) <= rows
        is not satisifed.
        """
        if not util.within(0, y0, self.get_height()) or \
            not util.within(0, y1, self.get_height()):
            raise ValueError("y0 ({}) or y1 ({}) not within [0, {}] bounds"
                .format(y0, y1, self.get_height()))
        if y0 > y1:
            raise ValueError("y0 ({}) must be <= y1 ({})".format(y0, y1))
        if y0 == y1:
            return []

        filled = []
        for j in range(y1 - y0):
            if self.row_is_filled(y0 + j):
                filled.append(y0 + j)
        return filled

    def apply_multiplier(self, m: int):
        """Multiply all cell values by m."""
        self._grid = util.apply_multiplier(self._grid, m)
