class Snake {
  constructor(x, y, velocityX, velocityY, direction) {
    this.position = { x, y, length: 1, cells: [{ x, y }] };
    this.velocity = { x: velocityX, y: velocityY };
    this.direction = direction;
  }

  updatePosition() {
    const { x, y, velocityX, velocityY } = this.position;
    const newPosition = {
      x: x + velocityX,
      y: y + velocityY,
      length: this.position.length,
      cells: [...this.position.cells, { x: x + velocityX, y: y + velocityY }]
    };
    this.position = newPosition;
  }

  checkCollision() {
    const { x, y, length, cells } = this.position;
    if (x < 0 || x > 100 || y < 0 || y > 100) {
      return true;
    }
    for (let i = 1; i < length; i++) {
      if (cells[i].x === x && cells[i].y === y) {
        return true;
      }
    }
    return false;
  }
}