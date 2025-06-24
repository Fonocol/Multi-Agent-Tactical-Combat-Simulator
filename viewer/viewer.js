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
        this.highlightedEntities = new Set();
        this.trajectories = new Map();
        this.zoomLevel = 1;
        this.panOffset = { x: 0, y: 0 };
        this.isPanning = false;
        this.lastMousePos = { x: 0, y: 0 };

        // Create tooltip
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tooltip';
        document.body.appendChild(this.tooltip);

        // Enhanced color scheme
        this.agentColors = [
            '#00c8ff', '#1aff66', '#ff6bff', '#29abe2',
            '#ffcc00', '#00cec9', '#ff6666', '#9966ff'
        ];

        this.colorMap = {
            agent: '#00c8ff',
            target: '#00e600',
            danger: '#ff1a1a',
            energy: '#ffe600',
            enemy: '#e600ff',
            enemy_turret: '#8e44ad',
            enemy_kamikaze: '#e84393',
            projectile: '#ff3d00',
            mine: '#ff6f00',
            explosion: '#ffc400',
            objective: '#00fff7',
            smoke: '#aaaaaa',
            jammer: '#6c5ce7',
            wall: '#444444',
            decoy: '#fdcb6e',
            enemy_drone: '#d63031',
            enemy_drone_elite: '#be2edd',
            jammer_comunication: '#a29bfe',
            friendly: '#00c8ff',
            neutral: '#aaaaaa',
            hostile: '#ff1a1a'
        };

        this.currentEpisode = 'output';
        this.availableEpisodes = [];

        this.initControls();
        this.initCanvas();
        this.initEventListeners();
        this.discoverAvailableEpisodes().then(() => {
            this.loadData();
            this.initLegend();
            this.animate();
        });
    }

    initControls() {
        document.getElementById('playPauseBtn').addEventListener('click', () => this.togglePlay());
        document.getElementById('prevFrameBtn').addEventListener('click', () => this.prevFrame());
        document.getElementById('nextFrameBtn').addEventListener('click', () => this.nextFrame());
        document.getElementById('speedControl').addEventListener('input', (e) => {
            this.frameDelay = 1050 - e.target.value;
            document.getElementById('speedControl').style.setProperty('--thumb-color', this.getSpeedControlColor(e.target.value));
        });

        // Set initial thumb color
        const speedControl = document.getElementById('speedControl');
        speedControl.style.setProperty('--thumb-color', this.getSpeedControlColor(speedControl.value));
    }

    getSpeedControlColor(value) {
        // Convert value from 50-1000 to 0-1
        const normalized = (value - 50) / (1000 - 50);
        if (normalized < 0.3) return '#e74c3c'; // Red for slow
        if (normalized < 0.6) return '#f39c12'; // Orange for medium
        return '#2ecc71'; // Green for fast
    }

    initCanvas() {
        const container = this.canvas.parentElement;
        const size = Math.min(container.clientWidth, container.clientHeight) - 40;
        this.canvas.width = size;
        this.canvas.height = size;
        this.scale = size / 100 * this.zoomLevel;
    }

    initEventListeners() {
        // Mouse events
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mouseout', () => {
            this.hoveredEntity = null;
            this.tooltip.style.display = 'none';
        });

        // Zoom and pan events
        this.canvas.addEventListener('wheel', (e) => this.handleZoom(e));
        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 1 || (e.button === 0 && e.ctrlKey)) { // Middle click or Ctrl+Left click
                this.isPanning = true;
                this.lastMousePos = { x: e.clientX, y: e.clientY };
                this.canvas.style.cursor = 'grabbing';
            }
        });

        document.addEventListener('mouseup', () => {
            this.isPanning = false;
            this.canvas.style.cursor = 'default';
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (this.isPanning) {
                const dx = e.clientX - this.lastMousePos.x;
                const dy = e.clientY - this.lastMousePos.y;
                this.panOffset.x += dx / this.zoomLevel;
                this.panOffset.y += dy / this.zoomLevel;
                this.lastMousePos = { x: e.clientX, y: e.clientY };
                this.draw();
            }
        });

        // Double click to reset view
        this.canvas.addEventListener('dblclick', () => {
            this.zoomLevel = 1;
            this.panOffset = { x: 0, y: 0 };
            this.draw();
        });
    }

    async discoverAvailableEpisodes() {
        try {
            const response = await fetch('../data/available_episodes.json');
            this.availableEpisodes = await response.json();
            this.initEpisodeSelector();
        } catch (error) {
            console.error('Could not load episode list, using default', error);
            this.availableEpisodes = [{ id: 'episode_100', name: 'Episode 100' }];
            this.initEpisodeSelector();
        }
    }

    initEpisodeSelector() {
        const select = document.getElementById('episodeSelect');
        select.innerHTML = '';

        this.availableEpisodes.forEach(episode => {
            const option = document.createElement('option');
            option.value = episode.id;
            option.textContent = episode.name;
            select.appendChild(option);
        });

        select.value = this.currentEpisode;
        select.addEventListener('change', (e) => {
            this.currentEpisode = e.target.value;
            this.loadData();
        });
    }

    initLegend() {
        const legendContainer = document.getElementById('legendItems');
        legendContainer.innerHTML = '';

        // Group similar entities
        const entityGroups = {
            'Agents & Allies': ['agent', 'friendly'],
            'Enemies': ['enemy', 'enemy_turret', 'enemy_kamikaze', 'enemy_drone', 'enemy_drone_elite'],
            'Objects': ['target', 'energy', 'objective', 'decoy', 'mine', 'wall'],
            'Projectiles': ['projectile', 'explosion'],
            'Effects': ['smoke', 'jammer', 'jammer_comunication']
        };

        Object.entries(entityGroups).forEach(([groupName, types]) => {
            const groupHeader = document.createElement('div');
            groupHeader.className = 'legend-group-header';
            groupHeader.textContent = groupName;
            groupHeader.style.gridColumn = '1 / -1';
            groupHeader.style.marginTop = '0.5rem';
            groupHeader.style.marginBottom = '0.2rem';
            groupHeader.style.color = 'var(--accent-color)';
            groupHeader.style.fontWeight = '500';
            legendContainer.appendChild(groupHeader);

            types.forEach(type => {
                const item = document.createElement('div');
                item.className = 'legend-item';
                item.innerHTML = `
                    <span class="legend-color" style="background-color: ${this.colorMap[type]};"></span>
                    <span>${type.replace(/_/g, ' ')}</span>
                `;
                legendContainer.appendChild(item);
            });
        });
    }

    async loadData() {
        try {
            const response = await fetch(`../data/${this.currentEpisode}.json`);
            this.frames = await response.json();
            this.frameIndex = 0;
            this.trajectories.clear();
            this.updateFrameInfo();
            this.calculateTrajectories();

            // Reset view when loading new data
            this.zoomLevel = 1;
            this.panOffset = { x: 0, y: 0 };

        } catch (error) {
            console.error('Error loading simulation data:', error);
            alert('Failed to load simulation data. Please check console for details.');
        }
    }

    calculateTrajectories() {
        // Calculate trajectories for all agents
        for (let i = 0; i < this.frames.length; i++) {
            const frame = this.frames[i];
            frame.forEach(agentView => {
                const agent = agentView.agent;
                if (!this.trajectories.has(agent.id)) {
                    this.trajectories.set(agent.id, []);
                }
                this.trajectories.get(agent.id).push({
                    x: agent.x,
                    y: agent.y,
                    frame: i
                });
            });
        }
    }

    handleZoom(e) {
        e.preventDefault();
        const zoomIntensity = 0.1;
        const mouseX = e.clientX - this.canvas.getBoundingClientRect().left;
        const mouseY = e.clientY - this.canvas.getBoundingClientRect().top;

        // Convert mouse position to simulation coordinates
        const simX = (mouseX / this.scale) - this.panOffset.x;
        const simY = (mouseY / this.scale) - this.panOffset.y;

        // Calculate new zoom level
        const wheelDelta = e.deltaY < 0 ? 1 : -1;
        const newZoom = this.zoomLevel * (1 + wheelDelta * zoomIntensity);

        // Limit zoom level
        this.zoomLevel = Math.max(0.5, Math.min(5, newZoom));

        // Adjust pan offset to zoom at mouse position
        this.panOffset.x = (mouseX / (this.canvas.width / 100)) / this.zoomLevel - simX;
        this.panOffset.y = (mouseY / (this.canvas.height / 100)) / this.zoomLevel - simY;

        this.scale = (this.canvas.width / 100) * this.zoomLevel;
        this.draw();
    }

    drawGrid(spacing = 10) {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;

        // Adjust grid based on zoom level
        const effectiveSpacing = spacing * Math.max(1, Math.floor(1 / this.zoomLevel));

        for (let x = 0; x <= 100; x += effectiveSpacing) {
            this.ctx.beginPath();
            this.ctx.moveTo((x + this.panOffset.x) * this.scale, 0);
            this.ctx.lineTo((x + this.panOffset.x) * this.scale, 100 * this.scale);
            this.ctx.stroke();
        }

        for (let y = 0; y <= 100; y += effectiveSpacing) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, (y + this.panOffset.y) * this.scale);
            this.ctx.lineTo(100 * this.scale, (y + this.panOffset.y) * this.scale);
            this.ctx.stroke();
        }

        // Draw axes
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = 1.5;

        // X axis
        this.ctx.beginPath();
        this.ctx.moveTo((0 + this.panOffset.x) * this.scale, (50 + this.panOffset.y) * this.scale);
        this.ctx.lineTo((100 + this.panOffset.x) * this.scale, (50 + this.panOffset.y) * this.scale);
        this.ctx.stroke();

        // Y axis
        this.ctx.beginPath();
        this.ctx.moveTo((50 + this.panOffset.x) * this.scale, (0 + this.panOffset.y) * this.scale);
        this.ctx.lineTo((50 + this.panOffset.x) * this.scale, (100 + this.panOffset.y) * this.scale);
        this.ctx.stroke();
    }

    drawEntity(entity, color) {
        const x = (entity.x + this.panOffset.x) * this.scale;
        const y = (entity.y + this.panOffset.y) * this.scale;
        const radius = (entity.radius || 1) * this.scale / 1.0;

        // Draw trajectory if selected
        if (this.selectedAgent && entity.id === this.selectedAgent.id && this.trajectories.has(entity.id)) {
            this.drawTrajectory(entity.id, color);
        }

        // Draw entity
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, 2 * Math.PI);

        // Add glow effect for some entities
        if (['projectile', 'explosion', 'energy'].includes(entity.type)) {
            const glow = this.ctx.createRadialGradient(
                x, y, 0,
                x, y, radius * 1.5
            );
            glow.addColorStop(0, color);
            glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
            this.ctx.fillStyle = glow;
            this.ctx.fill();
        } else {
            this.ctx.fillStyle = color;
            this.ctx.fill();
        }

        // Add border for selected or hovered agent
        if ((this.selectedAgent && entity.id === this.selectedAgent.id) ||
            (this.hoveredEntity && entity.id === this.hoveredEntity.id)) {
            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        }

        // Draw label for important entities
        if (entity.type === 'agent' || entity.type.includes('enemy') ||
            this.highlightedEntities.has(entity.id)) {
            this.drawLabel(entity.type.replace('_', ' '), entity.x, entity.y, color);
        }
    }

    drawTrajectory(agentId, color) {
        const trajectory = this.trajectories.get(agentId);
        if (!trajectory || trajectory.length < 2) return;

        this.ctx.beginPath();
        this.ctx.moveTo(
            (trajectory[0].x + this.panOffset.x) * this.scale,
            (trajectory[0].y + this.panOffset.y) * this.scale
        );

        for (let i = 1; i < trajectory.length; i++) {
            this.ctx.lineTo(
                (trajectory[i].x + this.panOffset.x) * this.scale,
                (trajectory[i].y + this.panOffset.y) * this.scale
            );
        }

        this.ctx.strokeStyle = color + '80'; // Add transparency
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();

        // Draw position markers at regular intervals
        const markerInterval = Math.max(5, Math.floor(trajectory.length / 10));
        for (let i = 0; i < trajectory.length; i += markerInterval) {
            const point = trajectory[i];
            this.ctx.beginPath();
            this.ctx.arc(
                (point.x + this.panOffset.x) * this.scale,
                (point.y + this.panOffset.y) * this.scale,
                2, 0, 2 * Math.PI
            );
            this.ctx.fillStyle = color;
            this.ctx.fill();
        }
    }

    drawLabel(text, x, y, color = "#ffffff") {
        const canvasX = (x + this.panOffset.x) * this.scale;
        const canvasY = (y + this.panOffset.y) * this.scale;

        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(
            canvasX - 2,
            canvasY - 12,
            text.length * 6 + 4,
            14
        );

        this.ctx.fillStyle = color;
        this.ctx.font = "10px Arial";
        this.ctx.fillText(text, canvasX, canvasY);
    }

    drawDirection(x, y, angle, fov, length = 20, color = '#ffffff') {
        const canvasX = (x + this.panOffset.x) * this.scale;
        const canvasY = (y + this.panOffset.y) * this.scale;

        const endX = canvasX + length * this.scale * Math.cos(angle + fov / 2);
        const endY = canvasY + length * this.scale * Math.sin(angle + fov / 2);
        const endX1 = canvasX + length * this.scale * Math.cos(angle - fov / 2);
        const endY1 = canvasY + length * this.scale * Math.sin(angle - fov / 2);

        // Draw field of view cone
        this.ctx.beginPath();
        this.ctx.moveTo(canvasX, canvasY);
        this.ctx.lineTo(endX, endY);
        this.ctx.lineTo(endX1, endY1);
        this.ctx.closePath();
        this.ctx.fillStyle = color + '20';
        this.ctx.fill();

        // Draw direction lines
        this.ctx.beginPath();
        this.ctx.moveTo(canvasX, canvasY);
        this.ctx.lineTo(endX, endY);
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();

        this.ctx.beginPath();
        this.ctx.moveTo(canvasX, canvasY);
        this.ctx.lineTo(endX1, endY1);
        this.ctx.stroke();
    }

    drawHealthBar(x, y, radius, health, maxHealth = 100) {
        const canvasX = (x + this.panOffset.x) * this.scale;
        const canvasY = (y + this.panOffset.y) * this.scale;
        const barWidth = radius * this.scale * 1.5;
        const barHeight = 3;
        const healthPercent = health / maxHealth;

        // Background
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(
            canvasX - barWidth / 2,
            canvasY - radius * this.scale - 8,
            barWidth,
            barHeight
        );

        // Health bar
        this.ctx.fillStyle = healthPercent > 0.5 ? '#4CAF50' :
            healthPercent > 0.25 ? '#FFC107' : '#F44336';
        this.ctx.fillRect(
            canvasX - barWidth / 2,
            canvasY - radius * this.scale - 8,
            barWidth * healthPercent,
            barHeight
        );

        // Border
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(
            canvasX - barWidth / 2,
            canvasY - radius * this.scale - 8,
            barWidth,
            barHeight
        );
    }

    drawEnergyBar(x, y, radius, energy, maxEnergy = 100) {
        const canvasX = (x + this.panOffset.x) * this.scale;
        const canvasY = (y + this.panOffset.y) * this.scale;
        const barWidth = radius * this.scale * 1.5;
        const barHeight = 3;
        const energyPercent = energy / maxEnergy;

        // Background
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        this.ctx.fillRect(
            canvasX - barWidth / 2,
            canvasY - radius * this.scale - 4,
            barWidth,
            barHeight
        );

        // Energy bar
        this.ctx.fillStyle = '#2196F3';
        this.ctx.fillRect(
            canvasX - barWidth / 2,
            canvasY - radius * this.scale - 4,
            barWidth * energyPercent,
            barHeight
        );

        // Border
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(
            canvasX - barWidth / 2,
            canvasY - radius * this.scale - 4,
            barWidth,
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
        let totalHealth = 0;
        let totalEnergy = 0;

        // Draw all agent views
        frame.forEach((agentView, i) => {
            const agent = agentView.agent;
            const facing = agentView.facing;
            const color = this.agentColors[i % this.agentColors.length];

            if (agent.alive) {
                agentsAlive++;
                totalHealth += agent.health || 0;
                totalEnergy += agent.energy || 0;
            }

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
        const avgHealth = agentsAlive > 0 ? Math.round(totalHealth / agentsAlive) : 0;
        const avgEnergy = agentsAlive > 0 ? Math.round(totalEnergy / agentsAlive) : 0;
        this.updateStats(agentsAlive, objectsCount, avgHealth, avgEnergy);

        // Draw tooltip if hovering over an entity
        if (this.hoveredEntity) {
            this.drawTooltip(this.hoveredEntity);
        }
    }

    drawTooltip(entity) {
            const canvasX = (entity.x + this.panOffset.x) * this.scale + 15;
            const canvasY = (entity.y + this.panOffset.y) * this.scale - 15;

            this.tooltip.style.display = 'block';
            this.tooltip.style.left = `${canvasX}px`;
            this.tooltip.style.top = `${canvasY}px`;

            let html = `<strong>${entity.type.replace(/_/g, ' ')}</strong>`;
            html += `<div>Position: (${entity.x.toFixed(1)}, ${entity.y.toFixed(1)})</div>`;

            if (entity.health !== undefined) {
                html += `<div>Health: ${entity.health}${entity.maxHealth ? `/${entity.maxHealth}` : ''}</div>`;
        }

        if (entity.energy !== undefined) {
            html += `<div>Energy: ${entity.energy}</div>`;
        }

        if (entity.radius !== undefined) {
            html += `<div>Radius: ${entity.radius.toFixed(1)}</div>`;
        }

        // Add any additional properties
        for (const [key, value] of Object.entries(entity)) {
            if (!['id', 'x', 'y', 'health', 'energy', 'type', 'radius', 'alive', 'maxHealth'].includes(key)) {
                html += `<div>${key.replace(/_/g, ' ')}: ${value}</div>`;
            }
        }

        this.tooltip.innerHTML = html;
    }

    handleMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const canvasX = event.clientX - rect.left;
        const canvasY = event.clientY - rect.top;
        
        // Convert to simulation coordinates
        const x = (canvasX / this.scale) - this.panOffset.x;
        const y = (canvasY / this.scale) - this.panOffset.y;

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
                this.canvas.style.cursor = 'pointer';
                break;
            }

            // Check visible objects
            for (const obj of agentView.visible) {
                const objDistance = Math.sqrt((x - obj.x) ** 2 + (y - obj.y) ** 2);
                if (objDistance < (obj.radius || 1)) {
                    this.hoveredEntity = obj;
                    this.canvas.style.cursor = 'pointer';
                    break;
                }
            }

            if (this.hoveredEntity) break;
        }

        if (!this.hoveredEntity) {
            this.tooltip.style.display = 'none';
            this.canvas.style.cursor = this.isPanning ? 'grabbing' : 'default';
        }
    }

    handleCanvasClick(event) {
        if (!this.hoveredEntity) {
            this.selectedAgent = null;
            this.updateAgentDetails();
            return;
        }

        if (this.hoveredEntity.type === 'agent') {
            this.selectedAgent = this.hoveredEntity;
            this.updateAgentDetails();
        } else {
            // Toggle highlight for non-agent entities
            if (this.highlightedEntities.has(this.hoveredEntity.id)) {
                this.highlightedEntities.delete(this.hoveredEntity.id);
            } else {
                this.highlightedEntities.add(this.hoveredEntity.id);
            }
            this.draw();
        }
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
                <span>Type:</span>
                <span>${agent.type.replace(/_/g, ' ')}</span>
            </div>
            <div class="agent-property">
                <span>Position:</span>
                <span>(${agent.x.toFixed(1)}, ${agent.y.toFixed(1)})</span>
            </div>
            <div class="agent-property">
                <span>Health:</span>
                <span>${agent.health || 100}${agent.maxHealth ? `/${agent.maxHealth}` : ''}</span>
            </div>
            <div class="agent-property">
                <span>Energy:</span>
                <span>${agent.energy || 100}</span>
            </div>
        `;

        // Add any additional agent properties
        for (const [key, value] of Object.entries(agent)) {
            if (!['id', 'x', 'y', 'health', 'energy', 'type', 'radius', 'alive', 'maxHealth'].includes(key)) {
                html += `
                    <div class="agent-property">
                        <span>${key.replace(/_/g, ' ')}:</span>
                        <span>${value}</span>
                    </div>
                `;
            }
        }

        detailsContainer.innerHTML = html;
    }

    updateStats(agentsAlive, objectsCount, avgHealth, avgEnergy) {
        document.getElementById('agentsAlive').textContent = agentsAlive;
        document.getElementById('objectsCount').textContent = objectsCount;
        document.getElementById('avgHealth').textContent = avgHealth;
        document.getElementById('avgEnergy').textContent = avgEnergy;

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
        document.getElementById('simulationTime').textContent = `Time: ${(this.frameIndex * 0.1).toFixed(1)}s`;
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

        if (this.isPlaying && !this.animationId) {
            this.animate();
        }
    }

    nextFrame() {
        this.isPlaying = false;
        this.frameIndex = (this.frameIndex + 1) % this.frames.length;
        this.updateFrameInfo();
        this.draw();
    }

    prevFrame() {
        this.isPlaying = false;
        this.frameIndex = (this.frameIndex - 1 + this.frames.length) % this.frames.length;
        this.updateFrameInfo();
        this.draw();
    }
}

// Initialize the simulation viewer when the page loads
window.addEventListener('DOMContentLoaded', () => {
    const viewer = new SimulationViewer();
    
    // Expose viewer to console for debugging
    window.viewer = viewer;
});