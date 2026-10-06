import unittest
from live.settings import validate
class DataVolumeTests(unittest.TestCase):
    def test_bounded_growth(self):
        self.assertEqual(validate({"ted_target":10000,"ted_max_pages":44}),(10000,44))
        self.assertEqual(validate({}),(2000,12))
    def test_incomplete_or_unbounded_budgets_rejected(self):
        for data in [{"ted_target":0},{"ted_target":True},{"ted_target":15001,"ted_max_pages":61},{"ted_target":10000,"ted_max_pages":39},{"ted_target":10000,"ted_max_pages":61}]:
            with self.assertRaises(ValueError):validate(data)
