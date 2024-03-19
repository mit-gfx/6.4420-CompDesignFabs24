import numpy as np


def point_on_plane(origin: np.ndarray, normal: np.ndarray, point: np.ndarray) -> tuple[bool, float]:
    """
    Return the signed distance between a point `point` and a plane defined by `origin` and `normal`,
    as well as whether that point is within tolerance of being considered on the plane.

    origin: (3,)
    normal: (3,)
    point: (3,)
    """
    dist = np.dot(point - origin, normal)
    return (abs(dist) < 1e-6, dist)


def triangle_plane_intersection(triangle: np.ndarray, origin: np.ndarray, normal: np.ndarray) -> list[np.ndarray]:
    """
    Implement a function to intesect a triangle and a plane.

    Input: Triangle, Plane defined by its origin and normal
        triangle: (3, 3)
        origin: (3,)
        normal: (3,)
    Output: list of all intersections of triangle edges with the plane, where they exist.
        list[(3,)]

    Hint:
        - Use the provided `distance_to_plane()` function
        - Consider the case of no intersection
        - Consider how to avoid repeated intersection points in the returned list.
    """

    (onV1, distV1) = point_on_plane(origin, normal, triangle[0])
    (onV2, distV2) = point_on_plane(origin, normal, triangle[1])
    (onV3, distV3) = point_on_plane(origin, normal, triangle[2])

    intersections = []
    # If the vertices are directly on the plane, they are the intersection points.
    if onV1:
        intersections.append(triangle[0])
    if onV2:
        intersections.append(triangle[1])
    if onV3:
        intersections.append(triangle[2])

    # All vertices are coplanar and on the plane.
    if onV1 and onV2 and onV3:
        return intersections

    if onV1 and onV3:
        # Orientation consistency
        intersections = [triangle[2], triangle[0]]

    # Neither point is on the plane, but they are on opposite sides, so we
    # can linearly interpolate the intersection of the edge and the plane.
    def test_edge(onV1, onV2, dist1, dist2, v1, v2):
        if (not onV1) and (not onV2) and (dist1 > 0) != (dist2 > 0):
            d1 = abs(dist1)
            total = d1 + abs(dist2)
            t = d1 / total
            result = (v1 * (1.0 - t)) + (v2 * t)
            intersections.append(result)

    test_edge(onV1, onV2, distV1, distV2, triangle[0], triangle[1])
    test_edge(onV2, onV3, distV2, distV3, triangle[1], triangle[2])
    test_edge(onV3, onV1, distV3, distV1, triangle[2], triangle[0])
    return intersections


def closest_parameter_on_line(start: np.ndarray, end: np.ndarray, point: np.ndarray) -> float:
    """
    start, end, point: (2,)
    """
    l2 = np.linalg.norm(start - end)
    if l2 <= 1e-6:
        return 0.0
    return np.dot(point - start, end - start) / l2


def in_bounds(min: float, max: float, value: float) -> bool:
    return min <= value and value <= max


def dist_squared(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    p1, p2: (2,)
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return (dx * dx) + (dy * dy)


def line_line_intersection(a: np.ndarray, b: np.ndarray) -> list[tuple[np.ndarray, float]]:
    """
    # TODO: Extra Credit
    # Implement a function to intesect two lines. The lines are defined by segments, but
    # you should intersect the infinite mathematical lines those segments lie on. This may
    # result in 0, 1, or perhaps more intersections.
    #
    # Input: Line segments, each modelled as a pair of 2D vertices.
    #   a: (2, 2)
    #   b: (2, 2)
    # Output:
    #   List of pairs representing coordinates of all intersections between the segments,
    #   if any exist. Each pair contains the coordinate intersection position and its
    #   "parameter" `t` along the line defined by segment `a`. This parameter may be
    #   positive, negative, greater than 1, who knows.
    #
    # Hint:
    # - If the two segments are parallel, does that mean they don't intersect?
    # - https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    """
    result: list[tuple[np.ndarray, float]] = []
    return result
