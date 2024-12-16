# This is Task_21.py
class Solution(object):
    def minCut(self, s):
        n = len(s)
        cuts = [0] * n
        is_palindrome = [[False] * n for _ in range(n)]
        for i in range(n):
            cuts[i] = i
        for end in range(n):
            for start in range(end + 1):
                if s[start] == s[end] and (end - start <= 2 or is_palindrome[start + 1][end - 1]):
                    is_palindrome[start][end] = True
        for i in range(n):
            if is_palindrome[0][i]:
                cuts[i] = 0
            else:
                cuts[i] = cuts[i - 1] + 1
                for j in range(1, i):
                    if is_palindrome[j][i]:
                        cuts[i] = min(cuts[i], cuts[j - 1] + 1)
        return cuts[-1]

#https://leetcode.com/problems/palindrome-partitioning-ii/solutions/5195073/minimum-cuts-for-palindrome-partitioning/