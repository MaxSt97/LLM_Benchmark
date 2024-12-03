# This is Task_17.py

class Solution:
    def __init__(self):
        self.memo = {}

    def isScramble(self, s1, s2):
        if s1 == s2:
            return True
        if len(s1) != len(s2) or sorted(s1) != sorted(s2):
            return False
        if (s1, s2) in self.memo:
            return self.memo[(s1, s2)]
        for i in range(1, len(s1)):
            if (self.isScramble(s1[:i], s2[:i]) and self.isScramble(s1[i:], s2[i:])) or \
               (self.isScramble(s1[:i], s2[-i:]) and self.isScramble(s1[i:], s2[:-i])):
                self.memo[(s1, s2)] = True
                return True
        self.memo[(s1, s2)] = False
        return False

#https://leetcode.com/problems/scramble-string/solutions/5795476/very-easy-python-solution/
