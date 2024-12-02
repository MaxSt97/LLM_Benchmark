from collections import Counter


class Solution:
    def maxPoints(self, points):
        def calculate_gcd(a, b):
            return a if b == 0 else calculate_gcd(b, a % b)

        num_points = len(points)
        if num_points <= 2:
            return num_points  # All points are on a line if there are two or fewer points.

        max_points_on_line = 1  # At least one point is always on a line.

        for i in range(num_points):
            x1, y1 = points[i]
            slopes = Counter()  # Counter to track the number of points for each slope
            for j in range(i + 1, num_points):
                x2, y2 = points[j]
                delta_x = x2 - x1
                delta_y = y2 - y1
                gcd_value = calculate_gcd(delta_x, delta_y)

                # Reduce the slope to its simplest form to count all equivalent slopes together.
                slope = (delta_x // gcd_value, delta_y // gcd_value)

                # Increment the count for this slope and update the maximum if needed.
                slopes[slope] += 1
                max_points_on_line = max(max_points_on_line, slopes[slope] + 1)

        return max_points_on_line


#https://leetcode.com/problems/max-points-on-a-line/solutions/6076037/max-point-on-a-line-with-code-explain-in-python/
