import unittest
from game.playfield import Step, PlayField

# Very small class, so we include it in the same test module
class TestStep(unittest.TestCase):

    def test_init(self):
        self.assertEqual(Step.vertical().get_type(), "vertical")
        left = Step.horizontal(True)
        right = Step.horizontal(False)
        self.assertEqual(left.get_value(), -1)
        self.assertEqual(right.get_value(), 1)
        for h_step in left, right:
            self.assertEqual(h_step.get_type(), "horizontal")
        rotate1 = Step.rotate()
        rotate2 = Step.rotate(2)
        self.assertEqual(rotate1.get_value(), 1)
        self.assertEqual(rotate2.get_value(), 2)
        for r_step in rotate1, rotate2:
            self.assertEqual(r_step.get_type(), "rotate")


class TestPlayField(unittest.TestCase):

    def setUp(self):
        self.mock_block = {"O": [[1, 1], [1, 1]]}

    def get_empty(self, spos = None):
        return PlayField(self.mock_block, "O",
            spawn_position=spos)

    def test_get_spawn_position(self):
        field = self.get_empty()
        self.assertEqual(10 // 2, field._active.x)
        self.assertEqual(0, field._active.y)

    def test_step(self):
        # both _try_step and step
        field = self.get_empty()
        LEFT = Step.horizontal(True)
        RIGHT = Step.horizontal(False)
        DOWN = Step.vertical()
        self.assertIsNotNone(field._try_step(DOWN))
        self.assertIsNotNone(field._try_step(LEFT))
        self.assertIsNotNone(field._try_step(RIGHT))
        self.assertTrue(field.step(DOWN))
        self.assertTrue(field.step(RIGHT))
        self.assertTrue(field.step(DOWN))
        tleft = self.get_empty((0, 0))
        self.assertIsNone(tleft._try_step(LEFT))
        self.assertIsNotNone(tleft._try_step(RIGHT))
        filled = self.get_empty()
        filled._field.fill_row(2, 1) # 3rd row from top is filled
        self.assertIsNone(filled._try_step(DOWN))
        self.assertFalse(filled.step(DOWN))
        self.assertTrue(filled.step(LEFT))

    def test_get_view(self):
        empty = self.get_empty()
        self.assertNotEqual(empty.get_view(), empty._field)
