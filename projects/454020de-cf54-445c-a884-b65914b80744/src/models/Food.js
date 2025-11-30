class Food {
  constructor(x, y, type) {
    this.x = x;
    this.y = y;
    this.type = type;
  }

  updatePosition(x, y) {
    this.x = x;
    this.y = y;
  }

  isCollisionWithSnake(snake) {
    return (this.x === snake.x && this.y === snake.y);
  }
}
