# This is Task_10.py
class Solution(object):
    def trap(self, height):
        l = len(height)

        if l > 2:
            nonwater = sum(height)

            left = 0
            right = l - 1

            leftwall = height[0]
            rightwall = height[l - 1]

            while left <= right:

                if height[left] <= height[right]:
                    if height[left] > leftwall:
                        leftwall = height[left]
                    else:
                        height[left] = leftwall

                    left += 1

                else:
                    if height[right] > rightwall:
                        rightwall = height[right]
                    else:
                        height[right] = rightwall

                    right -= 1

            return sum(height) - nonwater

        return 0

#https://leetcode.com/problems/trapping-rain-water/solutions/6053195/python-solution/