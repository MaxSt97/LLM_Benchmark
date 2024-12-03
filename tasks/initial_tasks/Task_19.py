# This is Task_19.py
class Solution:
    def maxProfit(self, prices):
        return self.solve(0, 1, prices, 0)

    def solve(self, ind, buy, prices, count):
        if ind == len(prices):
            return 0
        if count == 2:  # Maximum of two transactions
            return 0

        profit = 0
        if buy == 1 and count < 2:
            # Two options: buy or not buy
            # Buy
            op1 = -prices[ind] + self.solve(ind + 1, 0, prices, count)
            # Don't buy
            op2 = self.solve(ind + 1, 1, prices, count)
            profit = max(op1, op2)
        else:
            # Two options: sell or not sell
            # Sell
            op1 = prices[ind] + self.solve(ind + 1, 1, prices, count + 1)
            # Don't sell
            op2 = self.solve(ind + 1, 0, prices, count)
            profit = max(op1, op2)

        return profit

#https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/solutions/5946049/easy-to-understand-and-intuitive-recursive-and-memoization-approaches/