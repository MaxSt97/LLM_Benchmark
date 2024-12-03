# This is Task_03.py
class Solution(object):
    def isMatch(self, s, p):
        """
        :type s: str
        :type p: str
        :rtype: bool
        """
        memo = {}
        def dp(i, j):
            if (i, j) in memo: return memo[(i, j)]
            if j == len(p): result = i == len(s)
            else:
                match = i < len(s) and (p[j] == s[i] or p[j] == '.')
                if j + 1 < len(p) and p[j + 1] == '*':
                    result = (dp(i, j + 2) or (match and dp(i + 1, j)))
                else:
                    result = match and dp(i + 1, j + 1)
            memo[(i, j)] = result
            return result
        return dp(0, 0)

#https://leetcode.com/problems/regular-expression-matching/solutions/6082680/regex-recursion-and-memoization/