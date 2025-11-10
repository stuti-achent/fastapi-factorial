import math


def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is not available for negative numbers.")
    if n < 2:
        return 1
    return math.prod(range(2, n + 1))
