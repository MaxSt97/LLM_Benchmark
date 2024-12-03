# This is Task_22.py
class Solution(object):
    def checkaround(self, i, ratings):
        try:
            nextc = ratings[i + 1]
        except IndexError:
            nextc = float('inf')
        try:
            prevc = ratings[i - 1 if i > 0 else 9999999]
        except IndexError:
            prevc = float('inf')

        return prevc, nextc

    def candy(self, ratings):
        l = len(ratings)
        if l < 0:
            return 0

        give = [1] * l

        for i in range(1, l):
            prevn, nextn = self.checkaround(i, ratings)
            current = ratings[i]
            if current > prevn:
                give[i] = give[i - 1] + 1

        for i in range(l - 1, -1, -1):
            prevn, nextn = self.checkaround(i, ratings)
            current = ratings[i]

            if current > nextn:
                give[i] = max(give[i], give[i + 1] + 1)

        totalcandy = sum(give)
        return totalcandy


#https://leetcode.com/problems/candy/solutions/5923040/python-solution/