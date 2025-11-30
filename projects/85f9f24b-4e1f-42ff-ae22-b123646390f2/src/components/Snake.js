{"import React, { useState, useEffect } from 'react';
import * as THREE from 'three';

function Snake({ position, direction, grid }) {
  const [geometry, setGeometry] = useState(new THREE.BoxGeometry(1, 1, 1));
  const [material, setMaterial] = useState(new THREE.MeshBasicMaterial({ color: 0x00ff00 }));
  const [mesh, setMesh] = useState(new THREE.Mesh(geometry, material));

  useEffect(() => {
    mesh.position.set(position.x, position.y, position.z);
  }, [position]);

  const updatePosition = (newPosition) => {
    mesh.position.set(newPosition.x, newPosition.y, newPosition.z);
  };

  const updateDirection = (newDirection) => {
    direction = newDirection;
  };

  return (
    <group ref={mesh} scale={[1, 1, 1]} rotation={[0, 0, 0]} position={[position.x, position.y, position.z]}> 
      <mesh ref={mesh} geometry={geometry} material={material} /> 
    </group>
  );
}

export default Snake;