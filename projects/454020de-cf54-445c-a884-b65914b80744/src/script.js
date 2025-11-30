// Get the canvas element
var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');

// Set the canvas dimensions
canvas.width = 800;
canvas.height = 600;

// Define the snake and food variables
var snake = {
  x: 400,
  y: 300,
  dx: 10,
  dy: 0,
  length: 5,
  cells: []
};
var food = {
  x: Math.floor(Math.random() * (canvas.width - 20)) + 10,
  y: Math.floor(Math.random() * (canvas.height - 20)) + 10
};

// Draw the snake and food
function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'green';
  for (var i = 0; i < snake.length; i++) {
    ctx.fillRect(snake.cells[i].x, snake.cells[i].y, 20, 20);
  }
  ctx.fillStyle = 'red';
  ctx.fillRect(food.x, food.y, 20, 20);
}

// Update the snake position
function update() {
  snake.x += snake.dx;
  snake.y += snake.dy;
  snake.cells.push({
    x: snake.x,
    y: snake.y
  });
  if (snake.cells.length > snake.length) {
    snake.cells.shift();
  }
  if (snake.x < 0 || snake.x > canvas.width - 20 || snake.y < 0 || snake.y > canvas.height - 20) {
    alert('Game Over');
    return;
  }
  if (snake.x === food.x && snake.y === food.y) {
    snake.length++;
    food.x = Math.floor(Math.random() * (canvas.width - 20)) + 10;
    food.y = Math.floor(Math.random() * (canvas.height - 20)) + 10;
  }
}

// Handle key presses
document.addEventListener('keydown', function(event) {
  switch (event.key) {
    case 'ArrowUp':
      snake.dy = -10;
      snake.dx = 0;
      break;
    case 'ArrowDown':
      snake.dy = 10;
      snake.dx = 0;
      break;
    case 'ArrowLeft':
      snake.dx = -10;
      snake.dy = 0;
      break;
    case 'ArrowRight':
      snake.dx = 10;
      snake.dy = 0;
      break;
  }
});

// Main game loop
setInterval(function() {
  update();
  draw();
}, 100);
