import pygame
from pygame.locals import *

import unittest
from game import util


class TestUtil(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.font = pygame.font.SysFont(",".join(pygame.font.get_fonts()), 4)

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

    def test_resize(self):
        SIZE = (4, 4)
        TARGET_SIZES = [(5, 5), (1, 4), (3, 2)]
        dummy = pygame.Surface(SIZE)
        for target_size in TARGET_SIZES:
            rescaled = util.resize(dummy, target_size)
            self.assertEqual(rescaled.get_size(), target_size,
                "Resize should return Surface with expected target size")


    def test_fit(self):
        tall = pygame.Rect(0, 0, 50, 100)
        wide = pygame.Rect(0, 0, 100, 50)
        #big = pygame.Rect(0, 0, 150, 250)
        #small = pygame.Rect(0, 0, 25, 25)
        TABLE = [ # proportionKeep = True table
            # src, dest, expected output, proportionKeep
            tall, tall, tall, True,
            tall, wide, pygame.Rect(0, 0, 25, 50), True,
            wide, tall, pygame.Rect(0, 0, 50, 25), True,
            wide, tall, tall, False
        ]

        def table_tests(table):
            for i in range(0, len(table), 4):
                src = table[i]
                dest = table[i + 1]
                expected = table[i + 2]
                proportionKeep = table[i + 3]
                actual = util.fit(src, dest, proportionKeep)
                self.assertEqual(actual, expected,
                    "srcRect = " + str(src) + " | destRect = " + str(dest))
        table_tests(TABLE)

    def test_format_int(self):
        self.assertEqual("03", util.format_int(3, 2))
        self.assertEqual("45", util.format_int(45, 2))
        self.assertEqual("1000", util.format_int(1000, 3))

    def test_apply_multiplier(self):
        arr = [[0, 1, 0], [1, 0, 1]]
        self.assertListEqual(util.apply_multiplier(arr, 2),
            [[0, 2, 0], [2, 0, 2]])
