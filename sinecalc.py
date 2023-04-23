"""
A reloadable sine calculator.
"""
import math

from reloadable import Reloadable


class SineCalculatorLeeg(Reloadable):

    def calculate(self, x):
        # TODO: play here!
        return None


class SineCalculator(Reloadable):

    serialize_vars = (
        'last_res',
    )

    def __init__(self, state=None):
        self.last_res = 0
        super().__init__(state=state)

    def visualize(self, value):
        """Show a small bar graph for values between -1 and 1"""
        width = 20
        left_val = min(0, value)
        right_val = max(0, value)
        left_offset = int((left_val + 1) * width / 2)
        right_offset = int((right_val + 1) * width / 2)
        return f"|{' ' * left_offset}{'-' * (right_offset - left_offset)}{' ' * (width - right_offset)}|"

    def calculate(self, x):
        x = x % 6.28
        if x > 3.14:
            x = x - 6.28
        res = x - x**3 / 6 + x**5 / 120 - x**7 / 5040

        diff = self.last_res - res
        self.last_res = res

        return f"{x:5.1f} {res:9.6f} {self.visualize(res)} {diff:5.2f} cheat: {self.calculate_cheat(x)}"

    def calculate_cheat(self, x):
        return math.sin(x)

