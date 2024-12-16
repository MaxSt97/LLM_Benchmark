# This is Task_28.py
class Solution(object):
    def calculate(self, s):
        """
        :type s: str
        :rtype: int
        """
        stack = []  # To store (result, sign) pairs when encountering '('
        result = 0  # Current result
        num = 0  # Current number being processed
        sign = 1  # Current sign (+1 or -1)

        for char in s:
            if char.isdigit():
                # Build the current number
                num = num * 10 + int(char)
            elif char == '+':
                # Apply the previous number with the previous sign
                result += sign * num
                # Update the sign to +1 for the next number
                sign = 1
                num = 0  # Reset current number
            elif char == '-':
                # Apply the previous number with the previous sign
                result += sign * num
                # Update the sign to -1 for the next number
                sign = -1
                num = 0  # Reset current number
            elif char == '(':
                # Push the current result and sign to the stack
                stack.append(result)
                stack.append(sign)
                # Reset result and sign for the new sub-expression
                result = 0
                sign = 1
            elif char == ')':
                # Apply the current number
                result += sign * num
                num = 0  # Reset current number
                # Pop the sign and result from the stack and apply it
                result *= stack.pop()  # Multiply the result by the sign before '('
                result += stack.pop()  # Add the result before '('
            # Ignore spaces
        # Add any number left after finishing the loop
        result += sign * num
        return result

#https://leetcode.com/problems/basic-calculator/solutions/5780400/calculator/