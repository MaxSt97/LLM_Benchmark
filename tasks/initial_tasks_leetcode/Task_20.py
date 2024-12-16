# This is Task_20.py

class Solution(object):
    def maxPathSum(self, root):
        m = [-999999999]

        def check(root, m):
            if root is None:
                return 0
            l = max(0, check(root.left, m))
            r = max(0, check(root.right, m))
            m[0] = max(l + r + root.val, m[0])
            return max(l, r) + root.val

        res = check(root, m)
        return m[0]

#https://leetcode.com/problems/binary-tree-maximum-path-sum/solutions/5840440/beat-97-python-easy-solution-o-n/

