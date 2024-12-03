# This is Task_01.py
class Solution:
    def getPermutation(self, n: int, k: int) -> str:
        ans = []
        vis = [False] * (n + 1)
        for i in range(n):
            fact = 1
            for j in range(1, n - i):
                fact *= j
            for j in range(1, n + 1):
                if not vis[j]:
                    if k > fact:
                        k -= fact
                    else:
                        ans.append(str(j))
                        vis[j] = True
                        break
        return ''.join(ans)

#https://leetcode.com/problems/permutation-sequence/solutions/6062381/detailed-explanation-of-permutation-sequence-problem-with-many-programming-languages/

