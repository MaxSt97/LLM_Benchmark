# This is Task_13.py
class Solution(object):
    def isNumber(self, s):
        """
        :type s: str
        :rtype: bool
        """

        try:
            if s.lower() in ["nan", "inf", "-inf", "+inf", "infinity", "-infinity", "+infinity"]:
                return False
            float(s)
            return True
        except ValueError:
            return False

#https://leetcode.com/problems/valid-number/solutions/5933091/beats-100-simple-code-easy-to-understand/
