from scipy.sparse import spmatrix, csc_matrix

import igl
import numpy as np
import scipy as sp
from typeguard import typechecked


@typechecked
def linear_weights(V: np.ndarray, C: np.ndarray) -> np.ndarray:
    """
    Compute linear weights for vertices on a tetrahedral mesh.

    Params:
        * `V: array` - (Nx3) vertex positions, N = #vertices
        * `C: array` - (Hx3) handle positions, H = #handles

    Return value:
        * `W: array` - (NxH) linear weights
    """
    # Compute inverse pairwise distances between vertices and handles
    N, H = V.shape[0], C.shape[0]
    W = np.zeros((N, H))

    eps = 1e-14  # Epsilon
    float_max = np.finfo(np.float64).max  # Infinity

    ## Loop over all vertices and handles
    for i in range(N):
        for j in range(H):
            # Compute the distance between the i-th vertex and the j-th handle

            d = np.linalg.norm(V[i] - C[j])  # <--

            # Compute the inverse distance

            if d < eps:
                W[i, j] = float_max  # <--
            else:
                W[i, j] = 1 / d  # <--

    # Normalize weights
    W /= W.sum(axis=1, keepdims=True)
    return W


@typechecked
def quadratic_optimization(Q: spmatrix, b: np.ndarray, bc: np.ndarray, num_iters: int = 100) -> np.ndarray:
    """
    Solve the quadratic optimization problem where the result minimizes `0.5 * W^T * Q * W`.

    Params:
        * `Q: spmatrix` - (NxN) coefficient matrix, N = #vertices
        * `b: array` - (Hx1) indices of constrained vertices
        * `bc: array` - (HxH) weights at constrained vertices w.r.t. each handle

    Return value:
        * `W: array` - (NxH) optimization result
    """
    # Get #vertices and #handles
    N, H = Q.shape[0], bc.shape[1]

    # Functions for creating placeholder variables
    empty_spmatrix = lambda: csc_matrix((0, N))
    empty_vector = lambda: np.zeros((0, 1))

    # Placeholder variables
    B = np.zeros((N, H))
    Bi = np.zeros(N)
    Aeq, Aieq = empty_spmatrix(), empty_spmatrix()
    Beq, Bieq = empty_vector(), empty_vector()

    # Variable bounds
    lx = np.zeros(N)
    ux = np.ones(N)

    # Initial solve for preconditioning (iter 0)
    W = igl.min_quad_with_fixed(Q, B, b, bc, Aeq, Beq, True)  # type: ignore

    # Compute weights for all handles
    for i in range(H):
        # print(f"BBW: computing weights for handle {i + 1} / {H} ...")

        # Get the constraints and initial guess for handle i
        bci = np.ascontiguousarray(bc[:, i])
        Wi = np.ascontiguousarray(W[:, i])

        # Solve the quadratic optimization problem for the current handle
        _, Wi = igl.active_set(Q, Bi, b, bci, Aeq, Beq, Aieq, Bieq, lx, ux, Wi, Auu_pd=True, max_iter=num_iters - 1)  # type: ignore

        # Write results to the corresponding column of W
        W[:, i] = Wi

    return W


@typechecked
def bounded_biharmonic_weights(V: np.ndarray, T: np.ndarray, C: np.ndarray) -> np.ndarray:
    """
    Compute bounded biharmonic weights for vertices on a tetrahedral mesh.

    Params:
        * `V: array` - (Nx3) vertex positions, N = #vertices
        * `T: array` - (Tx4) vertex indices of tet elements, T = #elements
        * `C: array` - (Hx3) handle positions, H = #handles

    Return value:
        * `W: array` - (NxH) BBW matrix
    """

    # Get boundary conditions
    P = np.arange(len(C), dtype=np.int64)
    BE = np.zeros((0, 2), dtype=np.int64)
    CE = np.zeros((0, 2), dtype=np.int64)
    _, b, bc = igl.boundary_conditions(V, T.astype(np.int64), C.astype(np.double), P, BE, CE)  # type: ignore

    # print(V.shape)
    # print(T.shape)
    # print(b.shape)
    # print(bc.shape)
    bbw = igl.pyigl_classes.BBW(0, 20)  # type: ignore

    try:
        W = bbw.solve(V.astype("float64"), T.astype("int32"), b, bc)
    except TypeError:
        raise TypeError("You probably didn't make any handle changes?")
    except np.AxisError:
        raise np.AxisError("Maybe add another handle")

    # print(W)

    W /= W.sum(axis=1, keepdims=True)
    # print(W)

    return W
