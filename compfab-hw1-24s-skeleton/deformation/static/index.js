import { OrbitControls } from 'https://cdn.skypack.dev/three@0.133.1/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'https://cdn.skypack.dev/three@0.133.1/examples/jsm/controls/TransformControls.js';
import { STLLoader } from 'https://cdn.skypack.dev/three@0.133.1/examples/jsm/loaders/STLLoader.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const raycaster = new THREE.Raycaster();
const renderer = new THREE.WebGLRenderer();

const orbit = new OrbitControls(camera, renderer.domElement);
const control = new TransformControls(camera, renderer.domElement);

const stlLoader = new STLLoader();

const geometry = new THREE.BufferGeometry();
const material = new THREE.MeshNormalMaterial({ color: 0x88cdce });
const mesh = new THREE.Mesh(geometry, material);

const pointGeom = new THREE.SphereGeometry(1, 16, 16);
const pointMaterial = new THREE.MeshBasicMaterial({ color: 0xFFA500 });
const orgPointMaterial = new THREE.MeshBasicMaterial({ color: 0xFF0000 });


// ------------
// States

let dedupVertices = [];
let dedupFaces = [];
const handles = new Map();
let selectedHandleId = -1;

// ------------


function render() { renderer.render(scene, camera); }
function animate() {
  requestAnimationFrame(animate);
  orbit.update();
  renderer.render(scene, camera);
}

function loadMesh(meshURL) {
  stlLoader.load(meshURL,
    (loaded) => {
      geometry.copy(loaded);
      geometry.attributes.position.needsUpdate = true;
      // reset states
      const dedup = deduplicateVertices(geometry.getAttribute("position").array);
      dedupVertices = dedup.vertices;
      dedupFaces = dedup.faces;
      handles.forEach((v) => {
        scene.remove(v.updated);
        scene.remove(v.original);
      });
      handles.clear();
      scene.remove(control);
      selectedHandleId = -1;
      animate();
    },
    (xhr) => {
      document.getElementById("progress-file").value = (xhr.loaded / xhr.total) * 100;
      // console.log((xhr.loaded / xhr.total) * 100 + '% loaded'); 
    },
    (error) => { console.log(error); });
}

async function postData(url, data, mode = 'no-cors') {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: mode, // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
      // 'Access-Control-Allow-Origin': '*'
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });

  return response.json(); // parses JSON response into native JavaScript objects
}

// ------------------------
// Index transforms

// Deduplicate vertices.
// vertices: (F * 3 * 3) each group of three vertices is a face
// returns { vertices: (V * 3), faces: (F * 3) indexed into vertices }

/**
 * Deduplicate vertices.
 * @param {any[]} vertices - (F * 3 * 3) each group of three vertices is a face
 * @returns vertices: (V * 3), faces: (F * 3) indexed into vertices 
 */
const deduplicateVertices = (vertices) => {
  const dedupVertices = [];
  const vertexPosnToIndex = new Map();
  const faces = [];

  let i = 0;
  while (i < vertices.length) {
    // this is per face 
    const indices = [];

    for (let j = 0; j < 3; j++) {
      let x = vertices[i + j * 3];
      let y = vertices[i + j * 3 + 1];
      let z = vertices[i + j * 3 + 2];

      let key = `${x}${y}${z}`;
      if (vertexPosnToIndex.has(key)) {
        let idx = vertexPosnToIndex.get(key);
        indices.push(idx);
      } else {
        vertexPosnToIndex.set(key, dedupVertices.length);
        indices.push(dedupVertices.length);
        dedupVertices.push([x, y, z]);
      }
    }

    faces.push(indices);
    i += 9;
  }

  return { vertices: dedupVertices.flat(), faces: faces.flat() };
};

/**
 * Duplicate vertices
 * @param {any[]} vertices (V * 3)
 * @param {any[]} faces (F * 3) indexed into vertices
 * @returns {any[]} (F * 3 * 3)
 */
const duplicateVertices = (vertices, faces) => {
  const unindexed = [];
  for (let i = 0; i < faces.length; i++) {
    unindexed.push(vertices[faces[i] * 3]);
    unindexed.push(vertices[faces[i] * 3 + 1]);
    unindexed.push(vertices[faces[i] * 3 + 2]);
  }
  return unindexed;
};

// ------------------
// Double Click


// position: THREE.Vector3
let findClosestPoint = (position) => {
  // inf
  var closestDistance = Number.MAX_VALUE;
  let closest;
  let closestId = -1;

  for (let i = 0; i < dedupVertices.length / 3; i++) {
    let posn = new THREE.Vector3(dedupVertices[i * 3], dedupVertices[i * 3 + 1], dedupVertices[i * 3 + 2]);
    if (posn.distanceTo(position) < closestDistance) {
      closestDistance = posn.distanceTo(position);
      closest = posn;
      closestId = i;
    }
  }

  return { position: closest, id: closestId };
};

const handleDoubleClick = (event) => {
  const pointer = new THREE.Vector2();
  pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
  pointer.y = - (event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(pointer, camera);

  // calculate objects intersecting the picking ray
  const intersects = raycaster.intersectObject(mesh);

  if (intersects.length === 0) return;

  const click = intersects[0].point;
  const nearest = findClosestPoint(click);
  const nearest_v = nearest.position;
  const nearest_id = nearest.id;


  if (!handles.has(nearest_id)) {
    // construct
    // const geom = new THREE.SphereGeometry(1, 16, 16);
    const particle = new THREE.Mesh(pointGeom, pointMaterial);
    // const orgGeom = new THREE.SphereGeometry(1, 16, 16);
    const orgParticle = new THREE.Mesh(pointGeom, orgPointMaterial);
    particle.position.set(nearest_v.x, nearest_v.y, nearest_v.z);
    orgParticle.position.set(nearest_v.x, nearest_v.y, nearest_v.z);
    // particle.position.set(click.x, click.y, click.z);
    // particle.userData = { id: id };

    scene.add(particle);
    scene.add(orgParticle);
    handles.set(nearest_id, { updated: particle, original: orgParticle });
  }

  // attach control
  if (selectedHandleId !== -1) {
    control.detach(handles.get(selectedHandleId).updated);
  }
  selectedHandleId = nearest_id;
  control.attach(handles.get(selectedHandleId).updated);
  scene.add(control);
};

const handleDeleteHandle = (event) => {
  if (selectedHandleId !== -1) {
    const handle = handles.get(selectedHandleId);
    control.detach(handle.updated);
    scene.remove(handle.updated);
    scene.remove(handle.original);
    handles.delete(selectedHandleId);
    selectedHandleId = -1;
    scene.remove(control);
  }
};

const handleDeleteAllHandles = (event) => {
  handles.forEach((v, k) => {
    if (selectedHandleId === k) {
      control.detach(v.updated);
      scene.remove(control);
      selectedHandleId = -1;
    }
    scene.remove(v.updated);
    scene.remove(v.original);
  });
  handles.clear();
};

const handleDeform = async (type) => {
  const handleData = [];
  handles.forEach((v, k) => {
    handleData.push({
      vid: k,
      original: [v.original.position.x, v.original.position.y, v.original.position.z],
      updated: [v.updated.position.x, v.updated.position.y, v.updated.position.z]
    });
  });
  const data = {
    vertices: dedupVertices,
    faces: dedupFaces,
    handles: handleData
  };
  const result = await postData(`/${type}`, data);
  const updated = Float32Array.from(duplicateVertices(result.vertices, dedupFaces));
  geometry.setAttribute('position', new THREE.BufferAttribute(updated, 3));
};

const handleUndeform = (e) => {
  const updated = Float32Array.from(duplicateVertices(dedupVertices, dedupFaces));
  geometry.setAttribute('position', new THREE.BufferAttribute(updated, 3));
};


function init() {
  // setup viewport
  camera.lookAt(0, 20, 0);
  camera.position.z = 100;

  renderer.setSize(window.innerWidth, window.innerHeight);
  document.getElementById("container").appendChild(renderer.domElement);


  document.getElementById("file-mesh-upload").addEventListener("change", (e) => {
    var file = e.target.files[0];
    if (file) {
      var meshURL = URL.createObjectURL(e.target.files[0]);
      loadMesh(meshURL);
    }
  });

  scene.add(mesh);
  loadMesh("bunny_lowpoly.stl");

  // event listener
  control.addEventListener('change', render);
  control.addEventListener('dragging-changed', function (event) {
    orbit.enabled = !event.value;
  });
  window.addEventListener("dblclick", handleDoubleClick);

  document.getElementById("btn-delete-handle").onclick = handleDeleteHandle;
  document.getElementById("btn-delete-all-handles").onclick = handleDeleteAllHandles;
  document.getElementById("btn-deform-linear").onclick = (e) => handleDeform("linear");
  document.getElementById("btn-deform-bbw").onclick = (e) => handleDeform("bbw");
  document.getElementById("btn-undeform").onclick = handleUndeform;

  document.getElementById("slider-handle-size").addEventListener("input", (event) => {
    pointGeom.copy(new THREE.SphereGeometry(Number(event.target.value), 16, 16));
    pointGeom.attributes.position.needsUpdate = true;
  });
}

init();

