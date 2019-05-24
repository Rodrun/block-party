import unittest
from game import util


class TestUtil(unittest.TestCase):

    def test_get_points(self):
        # Test table
        TABLE = {
            # lvl, points for (1-4) lines
            "0": [40, 100, 300, 1200],
            "1": [80, 200, 600, 2400],
            "2": [120, 300, 900, 3600],
            "9": [400, 1000, 3000, 12000]
        }
        for level_key in TABLE:
            level = int(level_key)
            row = TABLE[level_key]
            for cleared in range(len(row)):
                actual = util.get_points(level, cleared + 1)
                expected = row[cleared]
                self.assertEqual(actual, expected,
                    "Expected {} instead of {} at level {}".format(
                        expected, actual, level
                    ))
        self.assertEqual(util.get_points(1, -1), 0)
        self.assertEqual(util.get_points(0, 5), 0)

    def test_format_int(self):
        self.assertEqual("03", util.format_int(3, 2))
        self.assertEqual("45", util.format_int(45, 2))
        self.assertEqual("1000", util.format_int(1000, 3))

    def test_apply_multiplier(self):
        arr = [[0, 1, 0], [1, 0, 1]]
        self.assertListEqual(util.apply_multiplier(arr, 2),
            [[0, 2, 0], [2, 0, 2]])

    def test_within(self):
        self.assertTrue(util.within(0, 5, 5.5))
        self.assertTrue(util.within(-1, -0.5, 0))
        self.assertFalse(util.within(0, 6, 5))
        with self.assertRaises(ValueError):
            util.within(1, 0, -1)
