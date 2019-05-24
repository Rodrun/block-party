from copy import copy


MULTIPLIER = [40, 100, 300, 1200]


def get_points(level: int, lines_cleared: int) -> int:
    """Calculate points from lines cleared."""
    points = 0
    if lines_cleared > 0 and lines_cleared <= 4:
        points = MULTIPLIER[lines_cleared - 1] * (level + 1)
    return points


def format_int(n: int, zeros: int = 7) -> str:
    """Format integer as zero-filled string."""
    return str(n).zfill(zeros)


def apply_multiplier(target: list, x: int) -> list:
    """Multiply all target values by x in a 2D list."""
    if x == 1 or len(target) < 1:
        return target
    result = []
    for j in range(len(target)):
        result_row = []
        for i in range(len(target[j])):
            value = target[j][i]
            result_row.append(value * x)
        result.append(result_row)
    return result


def within(low, x, high):
    """Test if x is within low and high bounds (low <= x <= high).
    ValueError is raised if low > high"""
    if low > high:
        raise ValueError("low ({}) > high ({})".format(low, high))
    return low <= x and x <= high
