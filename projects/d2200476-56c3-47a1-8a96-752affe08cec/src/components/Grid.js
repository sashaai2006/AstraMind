import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

const Grid = () => {
  const canvasRef = useRef();
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ canvas: canvasRef.current });

  const grid = [];
  for (let x = 0; x < 10; x++) {
    grid[x] = [];
    for (let y = 0; y < 10; y++) {
      grid[x][y] = [];
      for (let z = 0; z < 10; z++) {
        const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);
        const cubeMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
        cube.position.set(x - 5, y - 5, z - 5);
        scene.add(cube);
        grid[x][y][z] = cube;
      }
    }
  }

  useEffect(() => {
    const animate = () => {
      requestAnimationFrame(animate);
      camera.position.set(0, 0, 5);
      renderer.render(scene, camera);
    };
    animate();
  }, []);

  return (
    <div style={{ width: '100%', height: '100vh', overflow: 'hidden' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100vh' }} />
    </div>
  );
};

export default Grid;