console.log('Game initialized.');
// Get the canvas element
const canvas = document.getElementById('canvas');
// Get the 2D drawing context
const ctx = canvas.getContext('2d');

// Set the canvas dimensions
canvas.width = 400;
canvas.height = 400;

// Define the snake and food objects
let snake = {
  x: 200,
  y: 200,
  dx: 10,
  dy: 0,
  length: 1,
  body: [
    { x: 200, y: 200 },
  ],
};
let food = {
  x: Math.floor(Math.random() * (canvas.width - 10)) + 5,
  y: Math.floor(Math.random() * (canvas.height - 10)) + 5,
};

// Function to draw the snake and food
function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'green';
  ctx.fillRect(snake.x, snake.y, 10, 10);
  ctx.fillStyle = 'red';
  ctx.fillRect(food.x, food.y, 10, 10);
}

// Function to update the snake position
function update() {
  snake.x += snake.dx;
  snake.y += snake.dy;

  // Check for collision with the canvas edges
  if (snake.x < 0 || snake.x > canvas.width - 10 || snake.y < 0 || snake.y > canvas.height - 10) {
    console.log('Game Over!');
    return;
  }

  // Check for collision with the food
  if (snake.x === food.x && snake.y === food.y) {
    snake.length++;
    food.x = Math.floor(Math.random() * (canvas.width - 10)) + 5;
    food.y = Math.floor(Math.random() * (canvas.height - 10)) + 5;
  }
}

// Main game loop
function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

// Start the game loop
loop();
// Add event listeners for keyboard input
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowUp' && snake.dy !== 10) {
    snake.dx = 0;
    snake.dy = -10;
  } else if (e.key === 'ArrowDown' && snake.dy !== -10) {
    snake.dx = 0;
    snake.dy = 10;
  } else if (e.key === 'ArrowLeft' && snake.dx !== 10) {
    snake.dx = -10;
    snake.dy = 0;
  } else if (e.key === 'ArrowRight' && snake.dx !== -10) {
    snake.dx = 10;
    snake.dy = 0;
  }
})