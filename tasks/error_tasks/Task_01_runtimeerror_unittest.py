import unittest
from Task_01_runtimeerror import Solution as FaultySolution

class Solution:
    def getPermutation(self, n: int, k: int) -> str:
        ans = []
        vis = [False] * (n + 1)
        for i in range(n):
            fact = 1
            for j in range(1, n - i):
                fact *= j
            for j in range(1, n + 1):
                if not vis[j]:
                    if k > fact:
                        k -= fact
                    else:
                        ans.append(str(j))
                        vis[j] = True
                        break
        return ''.join(ans)

class TestGetPermutation(unittest.TestCase):
    def setUp(self):
        self.correct_solution = Solution()
        self.faulty_solution = FaultySolution()

    def test_cases(self):
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
            (5, 120, "54321"),
            (5, 60, "32541"),
            (5, 30, "25341"),
            (5, 90, "45132"),
            (5, 15, "14325"),
            (5, 45, "34152"),
        ]

        for n, k, expected in test_cases:
            with self.subTest(n=n, k=k):
                # Test the correct solution
                self.assertEqual(self.correct_solution.getPermutation(n, k), expected)
                
                # Test the faulty solution to raise an error
                with self.assertRaises(IndexError):
                    self.faulty_solution.getPermutation(n, k)

if __name__ == "__main__":
    unittest.main()