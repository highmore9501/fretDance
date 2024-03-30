import unittest
from src.utils.utils import verifyValidCombination


class TestUtils(unittest.TestCase):
    def test_verifyValidCombination(self):
        # 重复手指在不同品位
        result = [
            {'index': 4, 'fret': 3, 'finger': 1},
            {'index': 3, 'fret': 2, 'finger': 1},
            {'index': 2, 'fret': 0}
        ]
        self.assertEqual(verifyValidCombination(result), False)
        # 手指值小的手指，而Fret值反而大
        result = [
            {'index': 0, 'fret': 3, 'finger': 1},
            {'index': 1, 'fret': 2, 'finger': 2},
            {'index': 2, 'fret': 0}
        ]
        self.assertEqual(verifyValidCombination(result), False)
        # 空弦音自身上有手指
        result = [
            {'index': 2, 'fret': 0, 'finger': 1},
        ]
        self.assertEqual(verifyValidCombination(result), False)


if __name__ == "__main__":
    unittest.main()
