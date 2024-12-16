# This is Task_11.py
class Solution:
    def isMatch(self, s, p):
        """
        :type s: str
        :type p: str
        :rtype: bool
        """
        # Initialize the DP table
        dp = [[False] * (len(p) + 1) for _ in range(len(s) + 1)]
        dp[0][0] = True  # Empty pattern matches empty string

        # Fill the first row for patterns with leading '*'
        for j in range(1, len(p) + 1):
            if p[j - 1] == '*':
                dp[0][j] = dp[0][j - 1]

        # Fill the rest of the table
        for i in range(1, len(s) + 1):
            for j in range(1, len(p) + 1):
                if p[j - 1] == '*':
                    # '*' can match zero or more characters
                    dp[i][j] = dp[i][j - 1] or dp[i - 1][j]
                elif p[j - 1] == '?' or p[j - 1] == s[i - 1]:
                    # '?' matches any single character or exact character match
                    dp[i][j] = dp[i - 1][j - 1]

        return dp[len(s)][len(p)]

# Example Usage
solution = Solution()
print(solution.isMatch("aa", "a"))       # Output: False
print(solution.isMatch("aa", "*"))       # Output: True
print(solution.isMatch("cb", "?a"))      # Output: False

#https://leetcode.com/problems/wildcard-matching/solutions/6064242/wildcard-matching/