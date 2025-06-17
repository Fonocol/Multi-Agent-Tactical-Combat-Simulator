class SimulationViewer {
    constructor() {
        this.canvas = document.getElementById('simCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.scale = 5;
        this.frames = [];
        this.frameIndex = 0;
        this.isPlaying = true;
        this.animationId = null;
        this.lastFrameTime = 0;
        this.fps = 0;
        this.frameDelay = 200;
        this.hoveredEntity = null;
        this.selectedAgent = null;
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tooltip';
        document.body.appendChild(this.tooltip);

        this.agentColors = ['#00c8ff', '#1aff66', '#00e6e6', '#29abe2', '#00b894', '#00cec9'];

        this.colorMap = {
            agent: '#00c8ff', // Cyan clair
            target: '#00e600', // Vert néon (plus lisible)
            danger: '#ff1a1a', // Rouge vif (plus net que #ff3300)
            energy: '#ffe600', // Jaune soleil (plus chaud)
            enemy: '#e600ff', // Violet fluo (très visible)
            enemy_turret: '#8e44ad', // Violet foncé (fort contraste)
            enemy_kamikaze: '#e84393', // Rose éclatant (très distinctif)
            projectile: '#ff3d00', // Orange-rouge vif (explosif)
            mine: '#ff6f00', // Orange foncé (risque visible)
            explosion: '#ffc400', // Jaune-orange intense
            objective: '#00fff7', // Bleu-vert néon (différent de "agent")
            smoke: '#aaaaaa', // Gris plus clair (plus visible)
            jammer: '#6c5ce7', // Indigo électrique (pas trop saturé)
            wall: '#444444', // Gris foncé pour ne pas voler la vedette
            decoy: '#fdcb6e', // Jaune pâle (facile à distinguer)
            enemy_drone: '#d63031', // Rouge intense (différent de danger)
            enemy_drone_elite: '#be2edd', // Violet élite (plus luxueux)
            jammer_comunication: '#a29bfe' // Lavande électrique (visible mais calme)
        };


        this.initControls();
        this.initCanvas();
        this.loadData();
        this.initLegend();
        this.animate();
    }

    initControls() {
        document.getElementById('playPauseBtn').addEventListener('click', () => this.togglePlay());
        document.getElementById('prevFrameBtn').addEventListener('click', () => this.prevFrame());
        document.getElementById('nextFrameBtn').addEventListener('click', () => this.nextFrame());
        document.getElementById('speedControl').addEventListener('input', (e) => {
            this.frameDelay = 1050 - e.target.value; // Invert value for more intuitive control
        });
    }

    initCanvas() {
        // Set canvas size based on container
        const container = this.canvas.parentElement;
        const size = Math.min(container.clientWidth, container.clientHeight) - 40;
        this.canvas.width = size;
        this.canvas.height = size;
        this.scale = size / 100; // Assuming environment is 100x100 units

        // Add event listeners
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mouseout', () => {
            this.hoveredEntity = null;
            this.tooltip.style.display = 'none';
        });
    }

    initLegend() {
        const legendContainer = document.getElementById('legendItems');
        legendContainer.innerHTML = '';

        Object.entries(this.colorMap).forEach(([type, color]) => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `
                <span class="legend-color" style="background-color: ${color};"></span>
                <span>${type.replace('_', ' ')}</span>
            `;
            legendContainer.appendChild(item);
        });
    }

    async loadData() {
        try {
            const response = await fetch('../data/output.json');
            this.frames = await response.json();
            this.updateFrameInfo();
        } catch (error) {
            console.error('Error loading simulation data:', error);
        }
    }

    drawGrid(spacing = 10) {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;

        for (let x = 0; x <= 100; x += spacing) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.scale, 0);
            this.ctx.lineTo(x * this.scale, 100 * this.scale);
            this.ctx.stroke();
        }

        for (let y = 0; y <= 100; y += spacing) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.scale);
            this.ctx.lineTo(100 * this.scale, y * this.scale);
            this.ctx.stroke();
        }
    }

    drawEntity(entity, color) {
        this.ctx.beginPath();
        this.ctx.arc(
            entity.x * this.scale,
            entity.y * this.scale,
            (entity.radius || 1) * this.scale,
            0,
            2 * Math.PI
        );

        // Add glow effect for some entities
        if (['projectile', 'explosion', 'energy'].includes(entity.type)) {
            const glow = this.ctx.createRadialGradient(
                entity.x * this.scale,
                entity.y * this.scale,
                0,
                entity.x * this.scale,
                entity.y * this.scale,
                (entity.radius || 1) * this.scale * 1.5
            );
            glow.addColorStop(0, color);
            glow.addColorStop(1, 'rgb(255, 0, 0)');
            this.ctx.fillStyle = glow;
            this.ctx.fill();
        } else {
            this.ctx.fillStyle = color;
            this.ctx.fill();
        }



        // Add border for selected agent
        if (this.selectedAgent && entity.id === this.selectedAgent.id) {
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        }
    }

    drawLabel(text, x, y, color = "#ffffff") {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(
            x * this.scale - 2,
            y * this.scale - 12,
            text.length * 6 + 4,
            14
        );

        this.ctx.fillStyle = color;
        this.ctx.font = "10px Arial";
        this.ctx.fillText(text, x * this.scale, y * this.scale);
    }

    drawDirection(x, y, angle, fov, length = 20, color = '#ffffff') {
        const endX = x + length * Math.cos(angle + fov / 2);
        const endY = y + length * Math.sin(angle + fov / 2);
        const endX1 = x + length * Math.cos(angle - fov / 2);
        const endY1 = y + length * Math.sin(angle - fov / 2);

        this.ctx.beginPath();
        this.ctx.moveTo(x * this.scale, y * this.scale);
        this.ctx.lineTo(endX * this.scale, endY * this.scale);
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();

        this.ctx.beginPath();
        this.ctx.moveTo(x * this.scale, y * this.scale);
        this.ctx.lineTo(endX1 * this.scale, endY1 * this.scale);
        this.ctx.stroke();
    }

    drawHealthBar(x, y, radius, health, maxHealth = 100) {
        const barWidth = radius * this.scale * 1.5;
        const barHeight = 3;
        const healthPercent = health / maxHealth;

        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(
            x * this.scale - barWidth / 2,
            y * this.scale - radius * this.scale - 8,
            barWidth,
            barHeight
        );

        this.ctx.fillStyle = healthPercent > 0.5 ? '#4CAF50' :
            healthPercent > 0.25 ? '#FFC107' : '#F44336';
        this.ctx.fillRect(
            x * this.scale - barWidth / 2,
            y * this.scale - radius * this.scale - 8,
            barWidth * healthPercent,
            barHeight
        );
    }

    drawEnergyBar(x, y, radius, energy, maxEnergy = 100) {
        const barWidth = radius * this.scale * 1.5;
        const barHeight = 3;
        const energyPercent = energy / maxEnergy;

        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(
            x * this.scale - barWidth / 2,
            y * this.scale - radius * this.scale - 4,
            barWidth,
            barHeight
        );

        this.ctx.fillStyle = '#2196F3';
        this.ctx.fillRect(
            x * this.scale - barWidth / 2,
            y * this.scale - radius * this.scale - 4,
            barWidth * energyPercent,
            barHeight
        );
    }

    draw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        this.drawGrid(10);

        // Get current frame data
        const frame = this.frames[this.frameIndex];
        if (!frame) return;

        // Counters for stats
        let agentsAlive = 0;
        let objectsCount = 0;

        // Draw all agent views
        frame.forEach((agentView, i) => {
            const agent = agentView.agent;
            const facing = agentView.facing;
            const color = this.agentColors[i % this.agentColors.length];

            if (agent.alive) agentsAlive++;

            // Draw agent
            this.drawEntity(agent, color);
            this.drawHealthBar(agent.x, agent.y, agent.radius || 1, agent.health || 100);
            this.drawEnergyBar(agent.x, agent.y, agent.radius || 1, agent.energy || 100);

            // Draw facing direction
            if (facing) {
                this.drawDirection(facing.x, facing.y, facing.angle, facing.fov, facing.length, color);
            }

            // Draw visible objects
            agentView.visible.forEach(obj => {
                if (obj.alive !== false) {
                    objectsCount++;
                    const objColor = this.colorMap[obj.type] || '#ffffff';
                    this.drawEntity(obj, objColor);

                    if (obj.facing) {
                        this.drawDirection(obj.x, obj.y, obj.facing.angle, obj.facing.fov || 0, obj.facing.length || 10, objColor);
                    }

                    // Draw health for enemies
                    if (obj.health !== undefined) {
                        this.drawHealthBar(obj.x, obj.y, obj.radius || 1, obj.health, obj.maxHealth || 100);
                    }
                }
            });
        });

        // Update stats
        this.updateStats(agentsAlive, objectsCount);

        // Draw tooltip if hovering over an entity
        if (this.hoveredEntity) {
            this.drawTooltip(this.hoveredEntity);
        }
    }

    drawTooltip(entity) {
        const x = entity.x * this.scale + 15;
        const y = entity.y * this.scale - 15;

        this.tooltip.style.display = 'block';
        this.tooltip.style.left = `${x}px`;
        this.tooltip.style.top = `${y}px`;

        let html = `<strong>${entity.type.replace('_', ' ')}</strong>`;
        html += `<div>Position: (${entity.x.toFixed(1)}, ${entity.y.toFixed(1)})</div>`;

        if (entity.health !== undefined) {
            html += `<div>Health: ${entity.health}</div>`;
        }

        if (entity.energy !== undefined) {
            html += `<div>Energy: ${entity.energy}</div>`;
        }

        if (entity.radius !== undefined) {
            html += `<div>Radius: ${entity.radius.toFixed(1)}</div>`;
        }

        this.tooltip.innerHTML = html;
    }

    handleMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left) / this.scale;
        const y = (event.clientY - rect.top) / this.scale;

        const frame = this.frames[this.frameIndex];
        if (!frame) return;

        // Check if mouse is over any entity
        this.hoveredEntity = null;

        for (const agentView of frame) {
            // Check agent
            const agent = agentView.agent;
            const distance = Math.sqrt((x - agent.x) ** 2 + (y - agent.y) ** 2);
            if (distance < (agent.radius || 1)) {
                this.hoveredEntity = agent;
                break;
            }

            // Check visible objects
            for (const obj of agentView.visible) {
                const objDistance = Math.sqrt((x - obj.x) ** 2 + (y - obj.y) ** 2);
                if (objDistance < (obj.radius || 1)) {
                    this.hoveredEntity = obj;
                    break;
                }
            }

            if (this.hoveredEntity) break;
        }

        if (!this.hoveredEntity) {
            this.tooltip.style.display = 'none';
        }
    }

    handleCanvasClick(event) {
        if (!this.hoveredEntity || this.hoveredEntity.type !== 'agent') {
            this.selectedAgent = null;
            this.updateAgentDetails();
            return;
        }

        this.selectedAgent = this.hoveredEntity;
        this.updateAgentDetails();
    }

    updateAgentDetails() {
        const detailsContainer = document.getElementById('agentDetails');

        if (!this.selectedAgent) {
            detailsContainer.innerHTML = '<p>Select an agent to view details</p>';
            return;
        }

        const agent = this.selectedAgent;
        let html = `
            <div class="agent-property">
                <span>ID:</span>
                <span>${agent.id || 'N/A'}</span>
            </div>
            <div class="agent-property">
                <span>Position:</span>
                <span>(${agent.x.toFixed(1)}, ${agent.y.toFixed(1)})</span>
            </div>
            <div class="agent-property">
                <span>Health:</span>
                <span>${agent.health || 100}</span>
            </div>
            <div class="agent-property">
                <span>Energy:</span>
                <span>${agent.energy || 100}</span>
            </div>
        `;

        // Add any additional agent properties
        for (const [key, value] of Object.entries(agent)) {
            if (!['id', 'x', 'y', 'health', 'energy', 'type', 'radius'].includes(key)) {
                html += `
                    <div class="agent-property">
                        <span>${key}:</span>
                        <span>${value}</span>
                    </div>
                `;
            }
        }

        detailsContainer.innerHTML = html;
    }

    updateStats(agentsAlive, objectsCount) {
        document.getElementById('agentsAlive').textContent = agentsAlive;
        document.getElementById('objectsCount').textContent = objectsCount;

        // Calculate FPS
        const now = performance.now();
        if (this.lastFrameTime) {
            this.fps = Math.round(1000 / (now - this.lastFrameTime));
            document.getElementById('fpsCounter').textContent = this.fps;
        }
        this.lastFrameTime = now;
    }

    updateFrameInfo() {
        document.getElementById('currentFrame').textContent = `Frame: ${this.frameIndex + 1}/${this.frames.length}`;
        document.getElementById('simulationTime').textContent = `Time: ${this.frameIndex}s`;
    }

    animate() {
        this.draw();

        if (this.isPlaying) {
            setTimeout(() => {
                this.frameIndex = (this.frameIndex + 1) % this.frames.length;
                this.updateFrameInfo();
                this.animationId = requestAnimationFrame(() => this.animate());
            }, this.frameDelay);
        } else {
            this.animationId = requestAnimationFrame(() => this.animate());
        }
    }

    togglePlay() {
        this.isPlaying = !this.isPlaying;
        const btn = document.getElementById('playPauseBtn');
        btn.innerHTML = this.isPlaying ? '<i class="fas fa-pause"></i> Pause' : '<i class="fas fa-play"></i> Play';

        if (this.isPlaying) {
            this.animate();
        }
    }

    nextFrame() {
        this.frameIndex = (this.frameIndex + 1) % this.frames.length;
        this.updateFrameInfo();
        this.draw();
    }

    prevFrame() {
        this.frameIndex = (this.frameIndex - 1 + this.frames.length) % this.frames.length;
        this.updateFrameInfo();
        this.draw();
    }
}

// Initialize the simulation viewer when the page loads
window.addEventListener('DOMContentLoaded', () => {
    new SimulationViewer();
});