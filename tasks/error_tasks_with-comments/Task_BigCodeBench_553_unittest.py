import unittest
import matplotlib

class TestCases(unittest.TestCase):
    def test_non_empty_lists(self):
        """Test mit gültigen nicht-leeren Listen."""
        ax = task_func([1, 2, 3], ['A', 'B', 'C'])
        self.assertIsInstance(ax, matplotlib.axes.Axes)

    def test_empty_a_list(self):
        """Test mit einer leeren 'a' Liste."""
        ax = task_func([], ['A', 'B', 'C'])
        self.assertIsInstance(ax, matplotlib.axes.Axes)

    def test_empty_b_list(self):
        """Test mit einer leeren 'b' Liste."""
        ax = task_func([1, 2, 3], [])
        self.assertIsInstance(ax, matplotlib.axes.Axes)

    def test_both_lists_empty(self):
        """Test mit beiden Listen 'a' und 'b' leer."""
        ax = task_func([], [])
        self.assertIsInstance(ax, matplotlib.axes.Axes)

    def test_a_list_longer_than_columns(self):
        """Test mit einer 'a' Liste, die mehr Elemente hat als vordefinierte Spalten."""
        ax = task_func([1, 2, 3, 4, 5, 6], ['A', 'B'])
        self.assertIsInstance(ax, matplotlib.axes.Axes)

if __name__ == '__main__':
    unittest.main()