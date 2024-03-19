import numpy as np
import time
import trimesh
from trimesh import Trimesh
from typing import NamedTuple
from pathlib import Path
from typeguard import typechecked
import fire

from intersection import triangle_plane_intersection, dist_squared
from gcode import convert_to_gcode, write_contours


@typechecked
def slice_to_gcode(stl_in: str, gcode_out: str, dz: float) -> list[list[list[np.ndarray]]]:
    mesh = trimesh.load(stl_in)
    assert isinstance(mesh, Trimesh)
    mesh, bottom, top = transform_to_fit_bed(mesh)
    print(f"Slicing {stl_in} with slice height {dz:.3f}...")
    t_start = time.time()
    edges = slice_mesh(mesh, bottom, top, dz)
    t_slice = time.time()
    contours = create_contours(edges)
    t_contour = time.time()

    print(f"\tSliced into {len(contours)} layers, with {sum([len(l) for l in contours])} total contours.")
    print(f"\t[Slicing: {(t_slice - t_start):.3f}s, Stitching: {(t_contour - t_slice):.3f}s]")
    convert_to_gcode(gcode_out, contours)
    return contours


@typechecked
def transform_to_fit_bed(mesh: Trimesh) -> tuple[Trimesh, float, float]:
    # Compute the bounding box of our mesh
    obj_min = mesh.vertices.min(axis=0)
    obj_max = mesh.vertices.max(axis=0)

    # Hypothetical print bed
    bed_min = np.array([0, 0, 0])
    bed_max = np.array([220, 220, 100])

    # Scale model to fit the bed dimensions, and translate it to fit the center of the bed.
    bed_dim = bed_max - bed_min
    obj_dim = obj_max - obj_min

    scale = min(1.0, bed_dim[0] / obj_dim[0], bed_dim[1] / obj_dim[1], bed_dim[2] / obj_dim[2])
    obj_center = (obj_min + obj_max) / 2  # Get the center.
    obj_center[2] = obj_min[2]  # Drop it like it's hot.

    bed_center = (bed_min + bed_max) / 2
    bed_center[2] = bed_min[2]

    translation = bed_center - obj_center
    scaled_translation = obj_center * (1.0 - scale) + translation
    transform_matrix = trimesh.transformations.scale_and_translate(scale, scaled_translation)
    mesh.apply_transform(transform_matrix)

    bottom = obj_min[2] * scale + scaled_translation[2]
    top = obj_max[2] * scale + scaled_translation[2]
    return (mesh, bottom, top)


class Edge:
    def __init__(self, start: np.ndarray, end: np.ndarray):
        self.start = start  # (3,)
        self.end = end  # (3,)

    def __repr__(self) -> str:
        return f"({format_vertex(self.start)} -> {format_vertex(self.end)})"


def format_vertex(vtx: np.ndarray) -> str:
    return f"{vtx[0]:.1f},{vtx[1]:.1f},{vtx[2]:.1f}"


@typechecked
def slice_mesh(mesh: trimesh.Trimesh, bottom: float, top: float, dz: float) -> list[list[Edge]]:
    """
    Input:
      mesh, the triangle mesh to be sliced
      bottom, the bottom Z coordinate of the mesh.
      top, the top Z coordinate of the mesh.
      dz, the vertical distance between slicing layers.

    Output:
      intersection_edges, a list of edges (in no particular order) for each layer.

    Hint:
      1. Enumerate each plane.
      2. You should not intersect each triangle with each plane. Think about strategies to minimize the number
          of intersections. For a given triangle, how can we know in advance which planes it may intersect?
    """
    total_height = top - bottom
    num_layers = int(np.ceil(total_height / dz))
    slice_plane_heights = [bottom + h * dz for h in range(0, num_layers + 1)]
    plane_normal = np.array([0.0, 0.0, 1.0])

    filtered_triangles = [[] for _ in slice_plane_heights]

    for tri in mesh.triangles:
        # Determine which planes intersect this triangle by Z coordinates
        minZ = min(tri[0][2], tri[1][2], tri[2][2])
        maxZ = max(tri[0][2], tri[1][2], tri[2][2])

        z = minZ
        j = int(np.floor((z - bottom) / dz))
        while (j - 1) * dz < maxZ and j < len(slice_plane_heights):
            filtered_triangles[j].append(tri)
            j += 1

    intersection_edges = []

    for i, height in enumerate(slice_plane_heights):
        plane_origin = np.array([0.0, 0.0, height])

        slice_edges = []
        for tri in filtered_triangles[i]:  # For every triangle this plane intersects
            edges = []

            ix = triangle_plane_intersection(tri, plane_origin, plane_normal)
            if len(ix) >= 2:
                edges.append(Edge(ix[0], ix[1]))
                if len(ix) == 3:
                    edges.append(Edge(ix[1], ix[2]))
                    edges.append(Edge(ix[2], ix[0]))
            slice_edges.extend(edges)

        intersection_edges.append(slice_edges)

    return intersection_edges


@typechecked
def create_contours(intersection_edges: list[list[Edge]]) -> list[list[list[np.ndarray]]]:
    """
    TODO: 2.1
    Input:
        intersection_edges, the "edge soups" you created in `slice_mesh`.

    Output: 
        contours, a a 3D matrix of 3D vertices.
        contours[i] represents the i'th layer in your slice.
        contours[i][j] represents the j'th individual closed contour in the i'th layer.
        contours[i][j][k] is the k'th vertex of the j'th contour, and is itself a 1 x 3 matrix
        of X,Y,Z vertex coordinates. You should not "close" the contour by adding the start point back
        to the end of the list; this segment will be treated as implicitly present.

    Hints:
     1. Think of how to connect cutting edges. Remember that edges in the input "soup" may be in arbitrary
        orientations.
     2. Some edges may be isolated and cannot form a contour. Detect and remove these.
        Bonus (0 points): think about what causes this to happen.
     3. There can and will be multiple contours in a layer (this is why we have the [j] dimension).
        Think about how to detect and handle this case.
     4. Think about how to optimize this: is there a way we can identify neighboring edges faster than by
        looping over all the other edges to figure out which are connected to it?
    """
    layers: list[list[list[np.ndarray]]] = []

    for i, layer in enumerate(intersection_edges):
        # TODO: Your code here.
        #       Build potentially many contours out of a single layer by connecting edges.
        contours: list[list[np.ndarray]] = []
        layers.append(contours)

    return layers


@typechecked
def main(model_name: str, slice_height: float = 0.4):
    stl_file_path = Path(f"data/{model_name}.stl")
    gcode_file = Path(f"output/{model_name}.gcode")
    contour_file = Path(f"output/{model_name}_contour.txt")
    assert stl_file_path.exists(), f"{model_name} does not exist"

    Path("output").mkdir(exist_ok=True)

    contours = slice_to_gcode(str(stl_file_path), str(gcode_file), slice_height)
    write_contours(str(contour_file), contours)


if __name__ == "__main__":
    fire.Fire(main)
