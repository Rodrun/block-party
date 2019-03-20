import unittest
import copy

import pygame
from pygame.locals import *
from game import component


class TestText(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.font = pygame.font.SysFont(",".join(pygame.font.get_fonts()), 4)
        self.dummy = component.Text("dummy", self.font)

    def test_init(self):
        with self.assertRaises(AssertionError):
            component.Text("", None)

    def test_set_text(self):
        prev_surf = copy.copy(self.dummy.image)
        self.dummy.set_text("Not dummy")
        self.assertNotEqual(prev_surf, self.dummy.image)

    def test_set_font(self):
        with self.assertRaises(AssertionError):
            self.dummy.set_font(None)
