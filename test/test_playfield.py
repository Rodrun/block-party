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
    pass
