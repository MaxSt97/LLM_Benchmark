# This is Task_12.py
class Solution:
    def __init__(self):
        self.n = 0
        self.res = []
        self.temp = []

    def check(self, row, col):
        row1 = row - 1
        x = 1
        while row1 >= 0:
            if self.temp[row1][col] == 'Q':
                return False
            if col - x >= 0 and self.temp[row1][col - x] == 'Q':
                return False
            if col + x < self.n and self.temp[row1][col + x] == 'Q':
                return False
            row1 -= 1
            x += 1
        return True

    def help(self, row):
        if row >= self.n:
            self.res.append(self.temp[:])
            return
        temp1 = ['.'] * self.n
        for i in range(self.n):
            if self.check(row, i):
                temp1[i] = 'Q'
                self.temp.append("".join(temp1))
                self.help(row + 1)
                self.temp.pop()
                temp1[i] = '.'

    def solveNQueens(self, n):
        self.n = n
        self.res = []
        self.temp = []
        self.help(0)
        return self.res

#https://leetcode.com/problems/n-queens/solutions/6105761/100-beats-backtracking-simplest-explanation/

