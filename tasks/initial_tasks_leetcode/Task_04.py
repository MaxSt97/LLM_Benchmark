# This is Task_04.py
class Solution(object):
    def findSubstring(self, s, words):
        wrlen = len(words)
        lrlen = len(words[0])
        slen = len(s)
        max = wrlen * lrlen
        index = 0
        inlst = []
        for i in range(slen - max + 1):
            sub = s[i:i + max]
            if (sub[:lrlen] in words):
                index = i
                temp = [sub[i:i + lrlen] for i in range(0, max, lrlen)]
                if sorted(temp) == sorted(words):
                    inlst.append(index)
            else:
                continue
        return (inlst)

#https://leetcode.com/problems/substring-with-concatenation-of-all-words/solutions/5940575/python-solution-in-18-lines/