import unittest
from Task_01_logicerror import Solution

class TestPermutationSequence(unittest.TestCase):
    def setUp(self):
        self.solution = Solution()
        
    def test_permutation_sequence(self):
        test_cases = [
            (1, 1, "1"),
            (2, 1, "12"),
            (2, 2, "21"),
            (3, 1, "123"),
            (3, 2, "132"),
            (3, 3, "213"),
            (3, 4, "231"),
            (3, 5, "312"),
            (3, 6, "321"),
            (4, 1, "1234"),
            (4, 2, "1243"),
            (4, 3, "1324"),
            (4, 4, "1342"),
            (4, 5, "1423"),
            (4, 6, "1432"),
            (4, 7, "2134"),
            (4, 8, "2143"),
            (4, 9, "2314"),
            (4, 10, "2341"),
            (4, 11, "2413"),
            (4, 12, "2431"),
            (4, 13, "3124"),
            (4, 14, "3142"),
            (4, 15, "3214"),
            (4, 16, "3241"),
            (4, 17, "3412"),
            (4, 18, "3421"),
            (4, 19, "4123"),
            (4, 20, "4132"),
            (4, 21, "4213"),
            (4, 22, "4231"),
            (4, 23, "4312"),
            (4, 24, "4321"),
            (5, 1, "12345"),
            (5, 2, "12354"),
            (5, 3, "12435"),
            (5, 4, "12453"),
            (5, 5, "12534"),
            (5, 6, "12543"),
            (5, 7, "13245"),
            (5, 8, "13254"),
            (5, 9, "13425"),
            (5, 10, "13452"),
        ]

        for n, k, expected in test_cases:
            with self.subTest(n=n, k=k, expected=expected):
                self.assertEqual(self.solution.getPermutation(n, k), expected)

if __name__ == "__main__":
    unittest.main()