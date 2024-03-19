import numpy as np
from typing import Optional, Union
from dataclasses import dataclass
from functools import cache
import svgwrite
from svgwrite.shapes import Polygon
from pathlib import Path


@dataclass
class Tab:
    """
    A structure that represents a tab and a bend with respect to the parent tab.

    Hint: See figure 2 on some guidance to what parameters need to be put here.
    """

    parent: Optional["Tab"]
    children: list["Tab"]
    # TODO 3.2: Add attributes as needed.

    def __hash__(self):
        return id(self)

    @cache
    def compute_corner_points(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes the four corner points in 2D (2,) based on the attributes.

        Hint: You may want to specify the convention on how you order these points.
        Hint: You can call this function on the parent to help get started.
        """
        # TODO 3.2: Implement this function
        raise NotImplementedError()

    def compute_all_corner_points(self) -> list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """
        Computes all four corner points of all tabs in the current subtree.
        """
        cps = [self.compute_corner_points()]
        for child in self.children:
            cps.extend(child.compute_all_corner_points())
        return cps


def generate_root_tab() -> Tab:
    """
    Generate a new parent tab
    """
    # TODO: 3.2: Update the arguments and implement this function.
    raise NotImplementedError()


def generate_child_tab(parent: Tab) -> Tab:
    """
    Generate a child tab. Make sure to update the children of parent accordingly.
    """
    # TODO: 3.2: Update the arguments and implement this function.
    raise NotImplementedError()


def draw_svg(root_tab: Tab, output: Union[str, Path], stroke_width: float = 1):
    cps = root_tab.compute_all_corner_points()
    points = np.array(cps).reshape(-1, 2)
    min_point = points.min(axis=0)  # (2,)
    max_point = points.max(axis=0)  # (2,)
    points -= min_point
    points += 2 * stroke_width
    size = max_point - min_point  # (2,)
    size += 4 * stroke_width
    rects = points.reshape(-1, 4, 2)

    dwg = svgwrite.Drawing(str(output), size=(size[0], size[1]), profile="tiny")

    for rect in rects:
        dwg.add(Polygon(rect, stroke="black", fill="lightgray", stroke_width=stroke_width))

    dwg.save()
