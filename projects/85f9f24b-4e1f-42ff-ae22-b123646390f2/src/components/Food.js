
import React, { useState, useEffect } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';

const Food = () => {
  const { scene, camera, gl } = useThree();
  const [foodPosition, setFoodPosition] = useState(null);

  useEffect(() => {
    const foodGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const foodMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const food = new THREE.Mesh(foodGeometry, foodMaterial);

    const gridDimensions = 10;
    const gridSize = gridDimensions * 2;

    let x, y, z;
    do {
      x = Math.floor(Math.random() * gridSize) - gridDimensions;
      y = Math.floor(Math.random() * gridSize) - gridDimensions;
      z = Math.floor(Math.random() * gridSize) - gridDimensions;
    } while (x === 0 && y === 0 && z === 0);

    food.position.set(x, y, z);
    scene.add(food);

    setFoodPosition(food.position);

    return () => {
      scene.remove(food);
    };
  }, []);

  useEffect(() => {
    if (foodPosition) {
      const food = new THREE.Mesh(
        new THREE.SphereGeometry(0.5, 32, 32),
        new THREE.MeshBasicMaterial({ color: 0xff0000 })
      );
      food.position.copy(foodPosition);
      scene.add(food);
    }
  }, [foodPosition]);

  return null;
};

export default Food;
