console.log('3D Snake Game Loaded');

// Configuration
const GRID_SIZE = 15;
const CUBE_SIZE = 0.9;
 const SPEED = 150; // ms per move

// Game State
let snake = []; // Array of Mesh objects
let direction = new THREE.Vector3(1, 0, 0);
let nextDirection = new THREE.Vector3(1, 0, 0);
let food = null;
let score = 0;
let isGameOver = false;
let lastMoveTime = 0;

// Debug info
const debugDiv = document.createElement('div');
debugDiv.style.position = 'absolute';
debugDiv.style.bottom = '10px';
debugDiv.style.left = '10px';
debugDiv.style.color = 'yellow';
debugDiv.style.fontFamily = 'monospace';
document.body.appendChild(debugDiv);

// Three.js Setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x112233); // Dark Blue for debug visibility

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 25, 15); // Higher and further back
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('game-container').appendChild(renderer.domElement);

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(10, 20, 10);
scene.add(dirLight);

// Board (Grid)
const gridHelper = new THREE.GridHelper(GRID_SIZE * 2, GRID_SIZE);
scene.add(gridHelper);

// Axes Helper (to see orientation)
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

// Materials
const snakeMaterial = new THREE.MeshPhongMaterial({ color: 0x4ade80 });
const headMaterial = new THREE.MeshPhongMaterial({ color: 0x22c55e });
const foodMaterial = new THREE.MeshPhongMaterial({ color: 0xef4444 });

// Initialize Game
function initGame() {
    console.log("Initializing Game...");
    // Clear existing objects
    if (food) scene.remove(food);
    snake.forEach(segment => scene.remove(segment));
    
    snake = [];
    score = 0;
    isGameOver = false;
    direction.set(1, 0, 0);
    nextDirection.set(1, 0, 0);
    
    document.getElementById('score-display').textContent = `Score: ${score}`;
    const gameOverScreen = document.getElementById('game-over-screen');
    if(gameOverScreen) gameOverScreen.classList.add('hidden');

    // Create initial snake (head + 2 body parts)
    createSegment(0, 0, headMaterial); // Head
    createSegment(-1, 0, snakeMaterial);
    createSegment(-2, 0, snakeMaterial);

    spawnFood();
}

function createSegment(x, z, material) {
    const geometry = new THREE.BoxGeometry(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(x, CUBE_SIZE/2, z);
    scene.add(mesh);
    snake.push(mesh);
}

function spawnFood() {
    if (food) scene.remove(food);
    
    let validPosition = false;
    let x, z;
    let attempts = 0;
    
    while (!validPosition && attempts < 100) {
        attempts++;
        x = Math.floor(Math.random() * GRID_SIZE * 2) - GRID_SIZE;
        z = Math.floor(Math.random() * GRID_SIZE * 2) - GRID_SIZE;
        
        // Keep within grid bounds (-GRID_SIZE to GRID_SIZE)
        x = Math.max(-GRID_SIZE + 1, Math.min(GRID_SIZE - 1, x));
        z = Math.max(-GRID_SIZE + 1, Math.min(GRID_SIZE - 1, z));

        // Check if overlaps with snake
        validPosition = !snake.some(segment => 
            Math.round(segment.position.x) === x && 
            Math.round(segment.position.z) === z
        );
    }

    const geometry = new THREE.SphereGeometry(CUBE_SIZE/2, 16, 16);
    food = new THREE.Mesh(geometry, foodMaterial);
    food.position.set(x, CUBE_SIZE/2, z);
    scene.add(food);
}

function updateGame(time) {
    if (isGameOver) return;
    
    if (time - lastMoveTime > SPEED) {
        lastMoveTime = time;
        moveSnake();
    }
}

function moveSnake() {
    // Update direction
    direction.copy(nextDirection);

    // Calculate new head position
    const head = snake[0];
    const newX = Math.round(head.position.x + direction.x);
    const newZ = Math.round(head.position.z + direction.z);

    // Check Collisions
    // 1. Walls
    if (Math.abs(newX) >= GRID_SIZE || Math.abs(newZ) >= GRID_SIZE) {
        console.log("Game Over: Wall Collision");
        gameOver();
        return;
    }

    // 2. Self
    const selfCollision = snake.slice(0, -1).some(segment => 
        Math.round(segment.position.x) === newX && 
        Math.round(segment.position.z) === newZ
    );
    if (selfCollision) {
        console.log("Game Over: Self Collision");
        gameOver();
        return;
    }

    // 3. Food
    let grew = false;
    if (food && Math.round(food.position.x) === newX && Math.round(food.position.z) === newZ) {
        score += 10;
        document.getElementById('score-display').textContent = `Score: ${score}`;
        spawnFood();
        grew = true;
    }

    // Move Logic
    // If grew: add new segment at tail position (by not removing tail)
    // If not grew: move tail to head position
    
    if (grew) {
        const tail = snake[snake.length - 1];
        createSegment(tail.position.x, tail.position.z, snakeMaterial);
    }

    // Move body segments
    for (let i = snake.length - 1; i > 0; i--) {
        snake[i].position.copy(snake[i-1].position);
        // Reset material to body color if it was head
        snake[i].material = snakeMaterial;
    }

    // Move head
    head.position.set(newX, CUBE_SIZE/2, newZ);
    head.material = headMaterial;
}

function gameOver() {
    isGameOver = true;
    const screen = document.getElementById('game-over-screen');
    if(screen) screen.classList.remove('hidden');
}

// Input Handling
window.addEventListener('keydown', (e) => {
    if (isGameOver && e.code === 'Space') {
        initGame();
        return;
    }

    switch(e.key) {
        case 'ArrowUp':
            if (direction.z !== 1) nextDirection.set(0, 0, -1);
            break;
        case 'ArrowDown':
            if (direction.z !== -1) nextDirection.set(0, 0, 1);
            break;
        case 'ArrowLeft':
            if (direction.x !== 1) nextDirection.set(-1, 0, 0);
            break;
        case 'ArrowRight':
            if (direction.x !== -1) nextDirection.set(1, 0, 0);
            break;
    }
});

// Render Loop
function animate(time) {
    requestAnimationFrame(animate);
    updateGame(time);
    renderer.render(scene, camera);
    
    // Update debug info
    debugDiv.innerText = `Time: ${Math.floor(time)} | Score: ${score} | Snake: ${snake.length} | Pos: ${snake[0]?.position.x}, ${snake[0]?.position.z}`;
}

// Window Resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Start
initGame();
animate(0);
