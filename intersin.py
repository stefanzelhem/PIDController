"""An "interactive" sine calculator.

This is a toy implementation of a reloading calculator, intended to show how the `Reloadable` class works and how one
would use it.

This script, when called from the command line, will load the SineCalculator class and execute it once every
second. Whenever that class detects a change, it will reload. You can interactively implement different calculators.
"""
import time

from sinecalc import SineCalculator

if __name__ == '__main__':
    sinecalc = SineCalculator()
    i = 0

    while True:
        try:
            value = sinecalc.calculate(i)
            print(f"{i:4.1f}\t{value}")
            i += 0.1
        except Exception as e:
            print(f"--- could not calculate:\n  {e}")
        time.sleep(1)
        sinecalc = sinecalc.reload()

