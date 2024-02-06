import igl
import numpy as np
import tetgen
from flask import Flask, request, redirect
from flask_cors import CORS, cross_origin
from typing import TypedDict, cast
from typeguard import typechecked
import fire

from weights import linear_weights, bounded_biharmonic_weights


class Handle(TypedDict):
    vid: int  # mapped to vertices
    original: list[float]  # (3,)
    updated: list[float]  # (3,)


class DeformRequest(TypedDict):
    vertices: list[float]  # (V * 3)
    faces: list[int]  # (F * 3)
    handles: list[Handle]


app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

app = Flask(__name__)


def update_handles(handle_positions: np.ndarray, updated_handles: np.ndarray) -> np.ndarray:
    handle_transforms = []
    for index in range(len(updated_handles)):
        t = updated_handles[index] - handle_positions[index]  # transformation
        handle_transforms.append([1, 0, 0, 0, 1, 0, 0, 0, 1, t[0], t[1], t[2]])
    return np.array(handle_transforms).reshape(len(updated_handles) * 4, 3)


@typechecked
def deform(req: DeformRequest, mode: str) -> list[float]:
    """
    mode: "linear" or "bbw"
    return: (V * 3,) updated vertices
    """
    V = np.array(req["vertices"]).reshape(-1, 3)  # (V, 3)
    F = np.array(req["faces"]).reshape(-1, 3)  # (F, 3)

    gen = tetgen.TetGen(V, F)
    tet_V, tet_F = gen.tetrahedralize()
    assert isinstance(tet_V, np.ndarray)
    assert isinstance(tet_F, np.ndarray)

    original_handles = np.array([handle["original"] for handle in req["handles"]])
    updated_handles = np.array([handle["updated"] for handle in req["handles"]])

    if mode == "linear":
        W = linear_weights(tet_V, original_handles)
    elif mode == "bbw":
        W = bounded_biharmonic_weights(tet_V, tet_F, original_handles)
    else:
        raise ValueError(f"Unknown mode {mode}")

    lbs = igl.lbs_matrix(tet_V, W)  # type: ignore
    assert isinstance(lbs, np.ndarray)

    handle_transforms = update_handles(original_handles, updated_handles)
    updated_tet_V = lbs @ handle_transforms

    updated_V = updated_tet_V[: len(V)]
    return updated_V.flatten().tolist()


@app.route("/linear", methods=["POST"])
@cross_origin()
def deform_linear():
    req = DeformRequest(request.get_json(force=True))
    res = deform(req, "linear")
    return {"vertices": res}, 200, {"Content-Type": "application/json"}


@app.route("/bbw", methods=["POST"])
@cross_origin()
def deform_bbw():
    req = DeformRequest(request.get_json(force=True))
    res = deform(req, "bbw")
    return {"vertices": res}, 200, {"Content-Type": "application/json"}


@app.route("/")
@cross_origin()
def redirect_index():
    return redirect("/static/index.html", code=302)


def main(port: int = 3030):
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    fire.Fire(main)
