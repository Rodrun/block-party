import unittest
from game.grid import Grid


class TestGrid(unittest.TestCase):

    def test_from_data(self):
        zeros = [[0 for _ in range(3)] for __ in range(2)]
        g = Grid.from_data(zeros)
        self.assertEqual(g._grid, zeros)
        zeros[0][0] = 1
        self.assertNotEqual(g._grid, zeros)

    def test_equals(self):
        ones = Grid(2, 3, 1)
        zeros = Grid(2, 3)
        zeros2 = Grid(2, 3)
        zero_diff = Grid(3, 2)
        self.assertTrue(ones == ones)
        self.assertTrue(zeros == zeros2)
        self.assertFalse(zeros == ones)
        self.assertFalse(zeros == zero_diff)

    def test_point_within(self):
        g = Grid(2, 3)
        self.assertTrue(g.point_within(0, 0))
        self.assertTrue(g.point_within(0, g.get_height() - 1))
        self.assertFalse(g.point_within(0, g.get_height()))
        self.assertFalse(g.point_within(-1, 0))
        self.assertFalse(g.point_within(0, -1))

    def test_dimensions(self):
        g = Grid(2, 3)
        self.assertEqual(g.get_height(), 2)
        self.assertEqual(g.get_width(), 3)
        self.assertEqual(g.get_dimensions(), (3, 2))
        with self.assertRaises(ValueError):
            g = Grid(-1, 1)
            g = Grid(5, -3)
            g = Grid(-2, -3)
            g = Grid(0, 4)

    def test_can_fit(self):
        parent = Grid(4, 5)
        sub0 = Grid(1, 1) # Yes
        self.assertTrue(parent.can_fit(sub0)[0])
        sub1 = Grid(5, 4) # Yes, since its 0s it can be trimmed
        self.assertTrue(parent.can_fit(sub1)[0])
        sub2 = Grid(1, 1) # Yes
        self.assertTrue(parent.can_fit(sub2, 4, 3)[0])
        sub3 = Grid(parent.get_height(), parent.get_width()) # Yes
        self.assertTrue(parent.can_fit(sub3)[0])
        sub4 = Grid.from_data([[1] * 10]) # No, not trimmable to fit
        self.assertFalse(parent.can_fit(sub4)[0])
        sub5 = Grid(5, 5)
        sub5.fill_row(0, 1)
        self.assertTrue(parent.can_fit(sub5)[0])
        self.assertFalse(parent.can_fit(sub0, 6, 6)[0]) # Out of bounds
        negative = Grid.from_data([[0, 1], [0, 1]])
        nfits, gr, pos = parent.can_fit(negative, -1, 0)
        self.assertTrue(nfits)
        self.assertListEqual(gr._grid, [[1], [1]])
        self.assertTupleEqual(pos, (0, 0))

    def test_remove(self):
        parent = Grid(4, 4)
        parent.remove(True, 0)
        self.assertEqual(parent.get_dimensions(), (4, 3))
        parent.remove(True, parent.get_height() - 1)
        self.assertEqual(parent.get_dimensions(), (4, 2))
        parent.remove(False, 0)
        self.assertEqual(parent.get_dimensions(), (3, 2))
        parent.remove(False, 1)
        self.assertEqual(parent.get_dimensions(), (2, 2))

    def test_trim(self):
        l = Grid.from_data([[0, 0, 0],
                            [0, 1, 1],
                            [0, 1, 0]])
        x, y = l.trim()
        self.assertListEqual(l._grid, [
            [1, 1],
            [1, 0]
        ])
        self.assertTupleEqual((x, y), (1, 1))
        l.trim() # No more should be trimmed
        self.assertEqual(l.get_dimensions(), (2, 2))
        empty = Grid(3, 3)
        x, y = empty.trim()
        self.assertEqual(empty.get_dimensions(), (0, 0))
        self.assertTupleEqual((x, y), (0, 0))
        i = Grid.from_data([[1, 0], [1, 0]])
        i.trim()
        self.assertListEqual(i._grid, [
            [1], [1]
        ])
        one = Grid.from_data([[0, 0], [0, 1]])
        one.trim()
        self.assertListEqual(one._grid, [[1]])

    def test_has_conflict(self):
        # Should only have conflicts with >1x1 grids
        lshape = Grid.from_data([[1, 0], [1, 1]])
        self.assertFalse(lshape.has_conflict(Grid.from_data([[1]]), 1, 0))
        self.assertFalse(lshape.has_conflict(Grid.from_data([[0, 1], [0, 0]])))
        oshape = Grid.from_data([[1, 1], [1, 1]])
        self.assertTrue(oshape.has_conflict(Grid.from_data([[0, 0, 1], [0, 0, 0]])))
        self.assertFalse(oshape.has_conflict(Grid(2, 2)))
        self.assertTrue(oshape.has_conflict(Grid(3, 3), 5, 5))

    def test_merge(self):
        parent0 = Grid(2, 2)
        parent0.merge(Grid(1, 1, 1)) # 0, 0
        self.assertEqual(parent0._grid, [[1, 0], [0, 0]])
        parent0.merge(Grid(2, 2, -1)) # 0, 0
        self.assertEqual(parent0._grid, [[-1, -1], [-1, -1]])
        parent0.merge(Grid(1, 1, 2), 1, 0) # 1, 0
        parent1 = Grid(4, 4)
        parent1.merge(Grid(1, 1, 1), 3, 3)
        self.assertEqual(parent1.get_at(3, 3), 1)
        with self.assertRaises(ValueError):
            parentE0 = Grid(2, 1)
            parentE0.merge(Grid(3, 3))
            parentE0.merge(Grid(2, 3))
            parentE0.merge(Grid(3, 2))
            parentE0.merge(None)

    def test_rotate90(self):
        square = Grid.from_data([[1, 2],
                                 [4, 3]])
        square.rotate90()
        self.assertEqual(square._grid,
            [[4, 1],
             [3, 2]])
        thin = Grid(3, 1, 1)
        thin.rotate90()
        self.assertEqual(thin._grid,
            [[1, 1, 1]])
        thick = Grid(2, 3)
        thick.rotate90(2) # 180 degree
        self.assertEqual(thick.get_dimensions(), (3, 2))

    def test_set_row(self):
        g = Grid.from_data([[1, 2, 3], [4, 5, 6]])
        three = [9, -9, 3]
        g.set_row(0, three)
        self.assertEqual(g.get_row(0), three)
        with self.assertRaises(ValueError):
            g.set_row(-1, three)
            g.set_row(g.get_height(), three)
            g.set_row(g.get_height() + 1, three)
            g.set_row(0, [])
            g.set_row(0, [x for x in range(g.get_width() + 1)])
            g.set_row(0, [x for x in range(g.get_width() - 1)])
            g.set_row(1, [0])

    def test_get_rows(self):
        sample0 = Grid(2, 3)
        self.assertEqual(sample0.get_rows(0, 0), [[0, 0, 0]])
        self.assertEqual(sample0.get_rows(0, 1), sample0._grid)

    def test_get_cols(self):
        dummy = Grid.from_data([
            [1, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ])
        self.assertListEqual(dummy.get_cols(0, 2), [
            [1, 1, 0], [0, 0, 1], [0, 0, 0]
        ])
        self.assertListEqual(dummy.get_cols(1, 2), [
            [0, 0, 1], [0, 0, 0]
        ])

    def test_row_is_zero(self):
        zeros = Grid(1, 4)
        self.assertTrue(zeros.row_is_zero(0))
        ones = Grid(2, 3, 1)
        for y in range(ones.get_height()):
            self.assertFalse(ones.row_is_zero(y))
        somewhat_zeros = Grid.from_data([[0, 0, 0], [0, -1, 0]])
        self.assertFalse(somewhat_zeros.row_is_zero(1))

    def test_row_is_filled(self):
        self.assertTrue(Grid(1, 1, -1).row_is_filled(0))
        self.assertFalse(Grid(1, 4).row_is_filled(0))
        with self.assertRaises(ValueError):
            Grid(1, 1).row_is_filled(1)

    def test_shift_row(self):
        tbt = Grid.from_data([[1, 2], [3, 4]])
        tbt.shift_row(0, 1) # Shift row 0 to row 1
        self.assertEqual(tbt.get_row(1), [1, 2])
        # Previously shifted row should be reset to 0s
        self.assertEqual(tbt.get_row(0), [0, 0])

    def test_shift_rows(self):
        def _rows_are_zero(grid: Grid, y0: int, y1: int):
            """
            Check if rows y0 to y1 are zero filled.
            """
            for y in range(y1 - y0 + 1):
                if not grid.row_is_zero(y0 + y):
                    return False
            return True

        ones = Grid(4, 1, 1)
        # Shift down, leaving row 0 zero filled
        ones.shift_rows(0, 2, 1)
        self.assertTrue(ones.row_is_zero(0))
        # Shift back up, leaving the last row zero filled
        ones.shift_rows(1, 3, -1)
        self.assertTrue(ones.row_is_zero(ones.get_height() - 1))
        self.assertFalse(ones.row_is_zero(0))

        twos = Grid(6, 1)
        twos.set_row(1, [2])
        twos.set_row(2, [3])
        # Shift row 1-2 down by 2, leaving zeros in their prev spot
        twos.shift_rows(1, 2, 2)
        self.assertTrue(_rows_are_zero(twos, 1, 2))
        self.assertFalse(_rows_are_zero(twos, 3, 4))
        self.assertEqual(twos.get_row(3), [2])
        self.assertEqual(twos.get_row(4), [3])

        negative = Grid.from_data([[0], [0], [0], [1], [2], [3]])
        # Shift three rows with step of -3
        negative.shift_rows(3, 5, -3)
        self.assertEqual(negative.get_rows(0, 2), [[1], [2], [3]])
        self.assertTrue(_rows_are_zero(negative, 3, 5))

    def test_fill_row(self):
        g = Grid(2, 3)
        g.fill_row(0, 1)
        self.assertTrue(g.get_row(0) == [1, 1, 1])

    def test_get_filled_rows(self):
        g = Grid(4, 2)
        filled_rows = [0, 2, 3]
        for fr in filled_rows:
            g.fill_row(fr, 1)
        self.assertListEqual(g.get_filled_rows(0, 4), filled_rows)
        g = Grid(1, 1)
        self.assertListEqual(g.get_filled_rows(0, 1), [])
        # ValueError raise test on 1x1 grid
        with self.assertRaises(ValueError):
            g.get_filled_rows(-1, 0)
            g.get_filled_rows(0, -1)
            g.get_filled_rows(1, 2)
            g.get_filled_rows(0, 2)
            g.get_filled_rows(1, 0)
        # y0 not 0 test
        g = Grid(10, 2)
        for fr in [0, 8, 9]:
            g.fill_row(fr, 1)
        self.assertListEqual(g.get_filled_rows(1, 7), [])
        self.assertListEqual(g.get_filled_rows(5, 9), [8])
        self.assertListEqual(g.get_filled_rows(8, 10), [8, 9])