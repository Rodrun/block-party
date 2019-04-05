import unittest

from game import generator


class TestGenerator(unittest.TestCase):

    def test_make_bag(self):
        gen = generator.Generator(names=["I", "O", "T", "S", "Z"])
        bag = gen.make_bag()
        self.assertEqual(len(bag), gen.bag_size)
        # Test for non repetition per bag
        repeated = False
        used = set()
        for n in bag:
            if n in used:
                repeated = True
                break
            used.add(n)
        self.assertFalse(repeated,
            "bag contains repeated elements: {}".format(bag))

    def test_pop_front(self):
        gen = generator.Generator(names=["O"], preview_size=3)
        popped = gen.pop_front()
        self.assertEqual(popped, "O")
        self.assertGreaterEqual(len(gen.stack), gen.preview_size)
