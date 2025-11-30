{"import React, { useState, useEffect } from 'react';
import * as THREE from 'three';

const Snake = () => {
  const [snake, setSnake] = useState([]);
  const [direction, setDirection] = useState({ x: 1, y: 0 });
  const [food, setFood] = useState({ x: 0, y: 0 });
  const [score, setScore] = useState(0);

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas') });
    renderer.setSize(window.innerWidth, window.innerHeight);

    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
    const snakeBody = new THREE.Mesh(geometry, material);
    scene.add(snakeBody);

    const foodGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const foodMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const foodMesh = new THREE.Mesh(foodGeometry, foodMaterial);
    scene.add(foodMesh);

    function animate() {
      requestAnimationFrame(animate);
      snakeBody.position.x += direction.x;
      snakeBody.position.y += direction.y;

      if (snakeBody.position.x < 0 || snakeBody.position.x > 10 || snakeBody.position.y < 0 || snakeBody.position.y > 10) {
        alert('Game Over!');
        return;
      }

      if (snakeBody.position.x === foodMesh.position.x && snakeBody.position.y === foodMesh.position.y) {
        setScore(score + 1);
        setFood({ x: Math.floor(Math.random() * 10), y: Math.floor(Math.random() * 10) });
      }

      renderer.render(scene, camera);
    }

    animate();
  }, []);

  return (
    <div>
      <canvas id="canvas"></canvas>
      <p>Score: {score}</p>
    </div>
  );
};

export default Snake;