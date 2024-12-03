# This is Task_23.py
class Solution(object):
    def wordBreak(self, s, wordDict):
        """
        :type s: str
        :type wordDict: List[str]
        :rtype: List[str]
        """
        dicts = set(wordDict)
        result = []

        def backtrack(cur, path):
            if cur == '':
                result.append(' '.join(path))
                return
            word = ''
            for i, c in enumerate(cur):
                word += c
                if word in dicts:
                    backtrack(cur[i + 1:], path + [word])

        backtrack(s, [])
        return result

#https://leetcode.com/problems/word-break-ii/solutions/5479456/beats-98-43-of-solutions/