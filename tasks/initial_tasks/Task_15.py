# This is Task_15.py
class Solution(object):
    def minWindow(self, s, t):
        """
        :type s: str
        :type t: str
        :rtype: str
        """

        if t in s:
            return t

        freq_t = {}
        freq = {}
        minl = 0
        minr = len(s)

        for c in t:
            freq_t[c] = freq_t.get(c, 0) + 1

        count_t = len(freq_t)
        count = 0

        l = 0
        for r in range(len(s)):
            c = s[r]

            if c in t:
                freq[c] = freq.get(c, 0) + 1
                if freq[c] == freq_t[c]:
                    count += 1

            while count == count_t:
                if r - l < minr - minl:
                    minr = r
                    minl = l
                if s[l] in t:
                    freq[s[l]] -= 1
                    if freq[s[l]] < freq_t[s[l]]:
                        count -= 1
                l += 1

        return s[minl:minr + 1] if minr - minl < len(s) else ""

#https://leetcode.com/problems/minimum-window-substring/solutions/5834573/beats-95-super-easy-to-understand/