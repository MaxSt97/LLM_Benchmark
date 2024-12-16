# This is Task_27.py
class Solution(object):
    def containsNearbyAlmostDuplicate(self, nums, k, t):
        """
        :type nums: List[int]
        :type indexDiff: int
        :type valueDiff: int
        :rtype: bool
        """
        if t == 0 and len(set(nums)) == len(nums):
            return False
        b = {}
        w = t + 1
        for i, n in enumerate(nums):
            bi = n // w

            if bi in b:
                return True
            elif bi + 1 in b and abs(n - b[bi + 1]) < w:
                return True
            elif bi - 1 in b and abs(n - b[bi - 1]) < w:
                return True

            b[bi] = n
            if i >= k:
                del b[nums[i - k] // w]
        return False

#https://leetcode.com/problems/contains-duplicate-iii/solutions/5570326/python-code-beats-99-14/
