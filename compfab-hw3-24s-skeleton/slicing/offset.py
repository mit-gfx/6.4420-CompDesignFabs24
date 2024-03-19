import numpy as np
from pathlib import Path
from typeguard import typechecked
import fire

from gcode import load_contours, convert_to_gcode
from intersection import line_line_intersection


def offset_to_gcode(contour_file: str, output_gcode: str, layer: int, offset_distance: float, num_offsets: int) -> None:
    contours = load_contours(contour_file)
    layer_contours = contours[layer]
    offset_distances = [offset_distance * i for i in range(0, 1 + num_offsets)]
    offset_contours = [
        [offset_contour(make_ccw(contour), distance) for distance in offset_distances] for contour in layer_contours
    ]
    convert_to_gcode(output_gcode, offset_contours)


def is_ccw(contour: list[np.ndarray]) -> bool:
    total = 0.0
    for i in range(len(contour)):
        p = contour[i - 1]
        q = contour[i]
        total += (p[0] * q[1]) - (q[0] * p[1])
    return total > 0


def make_ccw(contour: list[np.ndarray]) -> list[np.ndarray]:
    return contour if is_ccw(contour) else list(reversed(contour))


def offset_contour(contour: list[np.ndarray], offset: float) -> list[np.ndarray]:
    """
    TODO: Extra Credit, Contour Offsetting
    Input:
        contour: a list of vertices (3,) representing a closed contour. You may assume that
                 all of these vertices share the same Z value.
        offset: a direction to offset by. A negative value indicates an "inward" offset.
                For the purposes of this assignment you may assume that the contour is
                oriented COUNTER-CLOCKWISE; which implies that the interior is on the
                left side of the edge if we consider the direction from start to end to
                be "forward".
    Output:
        the offset contour list[(3,)].
    """
    new_contour: list[np.ndarray] = []
    for i in range(len(contour)):
        # TODO: Your code here. You should implement the algorithm described in the write
        #       up, making use of the `line_line_intersection` function.
        # Hint: find each pair of adjacent edges, offset them perpendicularly,
        #       and build up a new contour from their intersections.
        pass

    return new_contour


def main(model_name: str, layer: int, offset_distance: float, num_offsets: int):
    contour_file = Path(f"output/{model_name}_contour.txt")
    offset_gcode = Path(f"output/{model_name}_offset.gcode")
    assert contour_file.exists(), f"{model_name} contour does not exist. Run slicer first."

    Path("output").mkdir(exist_ok=True)

    offset_to_gcode(str(contour_file), str(offset_gcode), layer, offset_distance, num_offsets)


if __name__ == "__main__":
    fire.Fire(main)
