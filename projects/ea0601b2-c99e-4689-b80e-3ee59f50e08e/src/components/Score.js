{"import React from 'react';
import { useThree } from '@react-three/fiber';

function Score() {
  const { camera } = useThree();
  const [score, setScore] = React.useState(0);

  React.useEffect(() => {
    const intervalId = setInterval(() => {
      setScore(score => score + 1);
    }, 1000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div style={{ position: 'absolute', top: 10, right: 10, fontSize: 24, fontFamily: 'monospace' }}>{`Score: ${score}`}</div>
  );
}

export default Score;