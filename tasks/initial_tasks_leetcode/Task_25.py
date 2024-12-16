# This is Task_25.py
class Solution(object):
    def findMin(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        n = len(nums)
        l, r = 0, n - 1
        index = float('inf')
        while l <= r:
            mid = l + (r - l) // 2
            if nums[mid] == nums[l] == nums[r]:
                index = min(index, nums[mid])
                l += 1
                r -= 1
            ## i am in the left side
            elif nums[mid] >= nums[l]:
                index = min(index, nums[l])
                l = mid + 1
            else:
                index = min(index, nums[mid])
                r = mid - 1
        return index

#https://leetcode.com/problems/find-minimum-in-rotated-sorted-array-ii/solutions/4059038/only-small-adjusment-on-the-ordinary-binary-search-100-give-it-a-try/
