# This is Task_05.py
class Solution(object):
    def longestValidParentheses(self, s):
        """
        :type s: str
        :rtype: int
        """
        stack = [-1]  # Initialize stack with a base index
        max_length = 0

        for i in range(len(s)):
            if s[i] == '(':
                stack.append(i)  # Push the index of '(' onto the stack
            else:
                stack.pop()  # Pop the last opening parenthesis index
                if not stack:
                    stack.append(i)  # Push the current index as the base for next valid substring
                else:
                    max_length = max(max_length, i - stack[-1])  # Calculate valid length

        return max_length