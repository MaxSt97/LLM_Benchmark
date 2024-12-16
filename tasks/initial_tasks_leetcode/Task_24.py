# This is Task_24.py#
class Solution(object):
    def maxPoints(self, points):
        """
        :type digits: List[int]
        :rtype: List[int]
        """
        length = len(points)
        max_points = 0
        for i in range(length):
            hashmap = {}

            for j in range(i + 1, length):
                denominator = points[i][0] - points[j][0]
                numerator = points[i][1] - points[j][1]
                slope = (
                    numerator / float(denominator)
                    if denominator != 0
                    else "inf"
                )

                if slope in hashmap:
                    hashmap[slope] += 1
                else:
                    hashmap[slope] = 1
            max_ = max(hashmap.values()) + 1 if hashmap else 1
            if max_ > max_points:
                max_points = max_

        return max_points

#https://leetcode.com/problems/max-points-on-a-line/solutions/5216565/python-solution-using-slopes/