{"import React from 'react';
import ReactDOM from 'react-dom';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

function App() {
  return (
    <Canvas style={{ width: '100%', height: '100vh' }} camera={{ position: [0, 0, 5] }}>
      <OrbitControls />
    </Canvas>
  );
}

ReactDOM.render(<React.StrictMode>
  <App />
</React.StrictMode>, document.getElementById('root'));
}