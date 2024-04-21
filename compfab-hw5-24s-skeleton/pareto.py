import numpy as np
from matplotlib import pyplot as plt
from typing import Union, Literal, Optional
from typeguard import typechecked
import fire
from pathlib import Path



def print_points(points):
    print("[" + ", ".join(f"[{pt[0]:.5f},{pt[1]:.5f}]" for pt in points) + "]")
    return None


def pareto_front(points: np.ndarray) -> np.ndarray:
    """
    Compute the Pareto front of a set of 2D points. Minimization is assumed for all properties.

    points: (n, 2)
    returns: (n_pareto, 2) in order of non-decreasing x
    """
    # TODO: 1.1
    return np.array([])


def pareto_brute_force(points: np.ndarray) -> np.ndarray:
    """
    Get the Pareto front by brute-force, O(n^2) algorithm, to serve as a correctness reference.

    points: (n, 2)
    returns: (n_pareto, 2) in order of non-decreasing x
    """
    dom = (points[:, None] >= points[None]).all(axis=2)
    num_points = len(points)
    dom[np.arange(num_points), np.arange(num_points)] = False
    pareto_gt = points[~dom.any(axis=1)]
    return pareto_gt[np.lexsort((pareto_gt[:, 1], pareto_gt[:, 0]))]


@typechecked
def main(
    *,
    n: int = 10,
    filename: Union[str, Path, None] = None,
    test: bool = True,
    verbose: Optional[bool] = None,
):
    if filename is None:
        points = np.random.uniform(0, 1, (n, 2))
    else:
        filename = Path(filename)
        assert filename.exists(), f"{filename} does not exist"
        points = np.load(filename)

    if verbose is None:
        verbose = filename is None

    if verbose:
        print("Input Points:")
        print_points(points)

    pareto_user = pareto_front(points)

    if verbose:
        print("Found Pareto Front:")
        print_points(pareto_user)

    fig, ax = plt.subplots(constrained_layout=True)
    ax.scatter(points[:, 0], points[:, 1])
    ax.scatter(pareto_user[:, 0], pareto_user[:, 1])
    if filename is None:
        ax.set_title(f"Random: {n} points")
        fname = f"random-{n}.png"
    else:
        assert isinstance(filename, Path)
        ax.set_title(filename.stem)
        fname = f"file-{filename.stem}.png"
    Path("output").mkdir(parents=True, exist_ok=True)
    fig.savefig(Path("output") / fname)

    if test:
        # Check correctness
        pareto_gt = pareto_brute_force(points)
        if np.allclose(pareto_gt, pareto_user):
            print("Your output matches the model solution.")
        else:
            print("Your output does not matches the model solution.")


# Unit test
if __name__ == "__main__":
    fire.Fire(main)
