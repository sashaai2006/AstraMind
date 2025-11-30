{"import React from 'react';
import ReactDOM from 'react-dom';
import * as THREE from 'three';

function App() {
  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <canvas id="canvas" width="800" height="600"></canvas>
    </div>
  );
}

ReactDOM.render(<React.StrictMode>
  <App />
</React.StrictMode>, document.getElementById('root'));

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("canvas") });
