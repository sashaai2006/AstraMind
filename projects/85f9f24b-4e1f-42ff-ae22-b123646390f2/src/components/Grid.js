import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

const Grid = () => {
  const canvasRef = useRef();
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current });
  const grid = [];

  useEffect(() => {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    for (let x = -10; x <= 10; x++) {
      for (let y = -10; y <= 10; y++) {
        for (let z = -10; z <= 10; z++) {
          const cube = new THREE.Mesh(geometry, material);
          cube.position.set(x, y, z);
          scene.add(cube);
          grid.push(cube);
        }
      }
    }

    camera.position.z = 5;
    function animate() {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    }
    animate();
  }, []);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100vh' }} />
    </div>
  );
};

export default Grid;