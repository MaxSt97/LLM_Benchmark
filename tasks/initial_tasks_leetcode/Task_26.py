# This is Task_26.py
class Solution(object):
    def calculateMinimumHP(self, dungeon):
        """
        :type dungeon: List[List[int]]
        :rtype: int
        """
        cache = {}

        def findHt(i, j):
            if (i, j) in cache:
                return cache[(i, j)]

            if i == len(dungeon) or j == len(dungeon[0]):
                return float('-inf')
            elif i == len(dungeon) - 1 and j == len(dungeon[0]) - 1:
                return 0 if dungeon[i][j] > 0 else dungeon[i][j]

            val1 = findHt(i + 1, j)
            if dungeon[i][j] + val1 > 0:
                val1 = 0
            else:
                val1 += dungeon[i][j]

            val2 = findHt(i, j + 1)
            if dungeon[i][j] + val2 > 0:
                val2 = 0
            else:
                val2 += dungeon[i][j]

            res = max(val1, val2)
            cache[(i, j)] = res

            return res

        ans = findHt(0, 0)

        return 1 if ans > 0 else abs(ans) + 1

#https://leetcode.com/problems/dungeon-game/solutions/4987580/python-solution-using-memoization/