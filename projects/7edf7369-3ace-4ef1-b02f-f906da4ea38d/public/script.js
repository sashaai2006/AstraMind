// Import required modules
import SnakeGame from './SnakeGame.js';

// Define unit tests
describe('Snake Game', () => {
  it('should create a new game', () => {
    const game = new SnakeGame();
    expect(game).toBeInstanceOf(SnakeGame);
  });

  it('should move the snake', () => {
    const game = new SnakeGame();
    game.moveSnake();
    expect(game.snake.x).toBeGreaterThan(0);
  });

  it('should check for collisions', () => {
    const game = new SnakeGame();
    game.checkCollisions();
    expect(game.gameOver).toBe(false);
  });
});