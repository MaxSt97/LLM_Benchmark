# This is Task_08.py
class Solution(object):

    def maxiNum(self, num1, num2):
        return num1 if (num1 > num2) else num2

    def miniNum(self, num1, num2):
        return num2 if (num1 > num2) else num1

    def largestRectangleArea(self, heights):
        """
        :type heights: List[int]
        :rtype: int
        """
        max = 0
        stack = []
        stack.append({"index": 0, "height": heights[0]})
        for i in range(1, len(heights)):
            c = -1

            while ((len(stack) != 0) and (heights[i] < stack[-1]["height"])):
                newIndex = stack[-1]["index"]
                max = self.maxiNum(stack[-1]["height"] * (i - newIndex), max)
                stack.pop()
                c = 0
            if (c == 0):
                stack.append({"index": newIndex, "height": heights[i]})
            else:
                stack.append({"index": i, "height": heights[i]})

        while (len(stack) != 0):
            max = self.maxiNum(max, stack[-1]["height"] * (len(heights) - stack[-1]["index"]))
            stack.pop()

        print(max)

        return max

#https://leetcode.com/problems/largest-rectangle-in-histogram/solutions/5854933/easy-and-understandable-solution/