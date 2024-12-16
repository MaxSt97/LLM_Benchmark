# This is Task_29.py
class Solution(object):
    def numberToWords(self, num):
        if num == 0:
            return "Zero"

        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        thousands = ["", "Thousand", "Million", "Billion"]

        def helper(n):
            if n == 0:
                return []
            elif n < 20:
                return [ones[n]]
            elif n < 100:
                return [tens[n // 10]] + helper(n % 10)
            else:
                return [ones[n // 100], "Hundred"] + helper(n % 100)

        result = []
        for i in range(len(thousands)):
            if num % 1000 != 0:
                result = helper(num % 1000) + ([thousands[i]] if i > 0 else []) + result
            num //= 1000

        return " ".join(result).strip()

#https://leetcode.com/problems/integer-to-english-words/solutions/5793802/solved-by-using-cycle-and-dictionary/
