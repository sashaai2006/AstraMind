// Import required modules
import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import SnakeGame from './SnakeGame';

// Test the game rendering
it('renders the game', () => {
  const { getByText } = render(<SnakeGame />);
  expect(getByText('Score: 0')).toBeInTheDocument();
});

// Test the game logic
it('increases score when eating food', () => {
  const { getByText } = render(<SnakeGame />);
  const scoreElement = getByText('Score: 0');
  fireEvent.click(scoreElement);
  expect(getByText('Score: 1')).toBeInTheDocument();
});