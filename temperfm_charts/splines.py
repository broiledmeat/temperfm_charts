from math import isclose, sqrt


def _slope(x, y):
    """
    :type x: tuple[float, float]
    :type y: tuple[float, float]
    :rtype: float
    """
    return (y[1] - x[1]) / (y[0] - x[0])


def _get_monotonic_finite_differences(points):
    """
    :type points: list[tuple[float, float]]
    :rtype: list[float] 
    """
    d = _slope(points[0], points[1])
    m = [d]

    for i in range(1, len(points) - 1):
        next_d = _slope(points[i], points[i + 1])
        m.append((d + next_d) / 2)
        d = next_d
    m.append(d)

    return m


def get_monotonic_spline_tangents(points):
    """
    :type points: list[tuple[float, float]]
    :rtype: list[tuple[float, float]]
    """
    diffs = _get_monotonic_finite_differences(points)

    for i in range(len(points) - 1):
        d = _slope(points[i], points[i + 1])

        if isclose(d, 0):
            diffs[i] = 0
            diffs[i + 1] = 0
            continue

        a = diffs[i] / d
        b = diffs[i + 1] / d

        s = a * a + b * b
        if s > 9:
            s = d * 3 / sqrt(s)
            diffs[i] = s * a
            diffs[i + 1] = s * b

    tangents = []

    for i in range(len(points)):
        s = (points[min(len(points) - 1, i + 1)][0] - points[max(0, i - 1)][0]) / (6 * (1 + diffs[i] * diffs[i]))
        tangents.append((s or 0, diffs[i] * s or 0))

    return tangents
