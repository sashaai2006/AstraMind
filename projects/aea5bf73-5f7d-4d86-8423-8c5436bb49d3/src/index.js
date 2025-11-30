{"import React from 'react';
import ReactDOM from 'react-dom';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import Snake from './Snake';
import Food from './Food';

function Game() {
  return (
    <Canvas style={{ width: '100%', height: '100vh' }} camera={{ position: [0, 0, 10] }}>
      <OrbitControls />
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <Snake />
      <Food />
    </Canvas>
  );
}

ReactDOM.render(<Game />, document.getElementById('root'));
}