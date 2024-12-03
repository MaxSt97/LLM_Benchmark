# This is Task_16.py
class Solution(object):
    def maximalRectangle(self, matrix):
        if not matrix or not matrix[0]:
            return 0

        n, m = len(matrix), len(matrix[0])
        height = [0] * (m + 1)
        result = 0

        for r in matrix:
            for i in range(m):
                height[i] = height[i] + 1 if r[i] == '1' else 0
            stack = [-1]
            for i in range(m + 1):
                while height[i] < height[stack[-1]]:
                    h = height[stack.pop()]
                    w = i - stack[-1] - 1
                    result = max(result, h * w)
                stack.append(i)

        return result

#https://leetcode.com/problems/maximal-rectangle/solutions/5386685/python-solution-with-87-efficiency/
