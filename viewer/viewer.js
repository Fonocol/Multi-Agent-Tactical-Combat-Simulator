const canvas = document.getElementById('simCanvas');
const ctx = canvas.getContext('2d');
const scale = 5;

const agentColors = ['#00ffcc', '#00ccff', '#66ffcc', '#33ccff'];
const colorMap = {
    target: '#00ff00',
    danger: '#ff3300',
    energy: '#ffff00',
    enemy: '#ff00ff',
    enemy_turret: '#aa00ff',
    enemy_kamikaze: '#ff0088',
    projectile: '#ff5555',
    mine: '#ff9900',
    explosion: '#ffaa00',
    objective: '#00ffff'
};

let frames = [];
let frameIndex = 0;
let isPlaying = true;

async function loadData() {
    const response = await fetch('../data/output.json');
    frames = await response.json();
    requestAnimationFrame(draw);
}

function drawGrid(spacing = 10) {
    ctx.strokeStyle = '#222';
    ctx.lineWidth = 1;
    for (let x = 0; x <= canvas.width; x += spacing * scale) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    for (let y = 0; y <= canvas.height; y += spacing * scale) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

function drawEntity(entity, color) {
    ctx.beginPath();
    ctx.arc(entity.x * scale, entity.y * scale, entity.radius, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
}

function drawLabel(text, x, y, color = "#ffffff") {
    ctx.fillStyle = color;
    ctx.font = "10px Arial";
    ctx.fillText(text, x * scale + 6, y * scale - 6);
}

function drawDirection(x, y, angle, fov, length = 20, color = '#ffffff') {
    const endX = x + length * Math.cos(angle + fov / 2);
    const endY = y + length * Math.sin(angle + fov / 2);
    const endX1 = x + length * Math.cos(angle - fov / 2);
    const endY1 = y + length * Math.sin(angle - fov / 2);

    ctx.beginPath();
    ctx.moveTo(x * scale, y * scale);
    ctx.lineTo(endX * scale, endY * scale);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(x * scale, y * scale);
    ctx.lineTo(endX1 * scale, endY1 * scale);
    ctx.stroke();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawGrid(10);

    const frame = frames[frameIndex];

    frame.forEach((agentView, i) => {
        const color = agentColors[i % agentColors.length];
        const agent = agentView.agent;
        const facing = agentView.facing;

        drawEntity(agent, color);
        drawLabel("agent", agent.x, agent.y, color);
        drawLabel(`energy:${agent.energy}`, agent.x, agent.y + 2, color);
        drawLabel(`health:${agent.health}`, agent.x, agent.y + 4, color);

        if (facing) {
            drawDirection(facing.x, facing.y, facing.angle, facing.fov, facing.length, color);
        }

        for (const obj of agentView.visible) {
            const objColor = colorMap[obj.type] || '#ffffff';
            drawEntity(obj, objColor);
            drawLabel(obj.type, obj.x, obj.y, objColor);

            if (obj.facing) {
                drawDirection(obj.x, obj.y, obj.facing.angle, obj.facing.fov || 0, obj.facing.length || 10, objColor);
            }
        }
    });

    if (isPlaying) {
        frameIndex = (frameIndex + 1) % frames.length;
        setTimeout(() => requestAnimationFrame(draw), 200);
    }
}

function togglePlay() {
    isPlaying = !isPlaying;
    if (isPlaying) requestAnimationFrame(draw);
}

function nextFrame() {
    frameIndex = (frameIndex + 1) % frames.length;
    draw();
}

function prevFrame() {
    frameIndex = (frameIndex - 1 + frames.length) % frames.length;
    draw();
}

loadData();