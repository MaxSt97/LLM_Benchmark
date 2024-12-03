# This is Task_09.py
class Solution(object):
    def firstMissingPositive(self, nums):
        nums = list(dict.fromkeys(nums))
        nums.sort()

        m = 1

        for i in range(len(nums)):
            if nums[i] >= 1:
                if m < nums[i]:
                    return m
                else:
                    m = m + 1
        return m

#https://leetcode.com/problems/first-missing-positive/solutions/6021009/first-missing-positive-python/