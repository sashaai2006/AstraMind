{"class": "Food", "methods": {
  "generateFood": function(gridSize) {
    let food = {
      x: Math.floor(Math.random() * gridSize),
      y: Math.floor(Math.random() * gridSize),
      z: Math.floor(Math.random() * gridSize)
    };
    return food;
  },
  "hasSnakeEaten": function(snake, food) {
    return snake.body.some(part => part.x === food.x && part.y === food.y && part.z === food.z);
  }
}}