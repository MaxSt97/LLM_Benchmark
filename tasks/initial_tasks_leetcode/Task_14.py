# This is Task_14.py
class Solution(object):
    def fullJustify(self, words, maxWidth):
        """
        :type words: List[str]
        :type maxWidth: int
        :rtype: List[str]
        """
        result = []
        line = []
        line_c = 0
        len_words = len(words)
        for i, word in enumerate(words):
            if (line_c + len(word) > maxWidth):
                result.append(self.justify(line, line_c, maxWidth=maxWidth))
                line = [word]
                line_c = len(word) + 1
            else:
                line_c += len(word) + 1
                line.append(word)
        last_line = self.justify(line, line_c, maxWidth=maxWidth, last_line=True)
        if last_line:
            result.append(last_line)
        return result

    def justify(self, line, line_c, maxWidth, last_line=False):
        if not line:
            return ""
        if maxWidth == line_c:
            space_to_add = len(line)
        else:
            space_to_add = maxWidth - line_c + len(line)
        if len(line) == 1 or last_line:
            line_formated = " ".join(line) + " " * (maxWidth - len(" ".join(line)))
            return line_formated
        else:
            line_formated = self.add_space(line, space_to_add)
            return line_formated

    def add_space(self, line, space_to_add):
        quotient, remain = divmod(space_to_add, len(line) - 1)
        spaces = [quotient] * (len(line) - 1)

        for i in range(remain):
            spaces[i] += 1
        spaces.append(space_to_add - sum(spaces))
        result = ""
        for i in range(len(line) - 1):
            result += line[i] + " " * spaces[i]
        result += spaces[-1]*" " + line[-1]
        return result

#https://leetcode.com/problems/text-justification/solutions/6076766/easy-solution-in-python-beats-100-run-time/