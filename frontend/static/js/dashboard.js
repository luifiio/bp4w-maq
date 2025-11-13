// WebSocket connection
console.log('=== Dashboard.js loading ===');
const socket = io();
console.log('Socket.IO initialized');

// DOM elements
const connectBtn = document.getElementById('connectBtn');
console.log('connectBtn:', connectBtn);
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const logBtn = document.getElementById('logBtn');
const statusDot = document.getElementById('connectionStatus');
const statusText = document.getElementById('statusText');
const logMessages = document.getElementById('logMessages');

// State
let isLogging = false;
let systemStatus = {
    connected: false,
    streaming: false,
    logging: false
};

// Initialize
window.addEventListener('load', () => {
    console.log('Window loaded event fired');
    addLog('Dashboard loaded', 'info');
    updateButtonStates();
    initChartTabs();
    console.log('Initialization complete');
});

// Chart tab switching
function initChartTabs() {
    const tabs = document.querySelectorAll('.chart-tab');
    const containers = document.querySelectorAll('.chart-container');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const chartType = tab.getAttribute('data-chart');
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active chart container
            containers.forEach(c => c.classList.remove('active'));
            document.querySelector(`[data-chart-content="${chartType}"]`).classList.add('active');
        });
    });
}

// Socket events
socket.on('connect', () => {
    console.log('Socket connected!');
    addLog('WebSocket connected', 'success');
});

socket.on('disconnect', () => {
    console.log('Socket disconnected!');
    addLog('WebSocket disconnected', 'error');
});

socket.on('status', (status) => {
    console.log('Status received:', status);
    systemStatus = status;
    updateUI();
});

socket.on('sensor_data', (data) => {
    console.log('Sensor data received:', data);
    updateGauges(data);
    updateCharts(data);
});

// Debug: catch all events
socket.onAny((eventName, ...args) => {
    console.log(`[Socket Event] ${eventName}:`, args);
});

// Button handlers
connectBtn.addEventListener('click', async () => {
    console.log('Connect button clicked, current status:', systemStatus.connected);
    if (!systemStatus.connected) {
        const result = await apiCall('/api/connect', 'POST');
        console.log('Connect result:', result);
        addLog('Connecting to serial port...', 'info');
    } else {
        await apiCall('/api/disconnect', 'POST');
        addLog('Disconnecting...', 'info');
    }
});

startBtn.addEventListener('click', async () => {
    console.log('Start button clicked');
    const result = await apiCall('/api/start', 'POST');
    console.log('Start result:', result);
    if (result && result.success) {
        addLog('Starting data acquisition...', 'success');
        systemStatus.streaming = true;
        updateButtonStates();
        console.log('Streaming started, systemStatus:', systemStatus);
    } else {
        addLog(result?.message || 'Failed to start - please connect first', 'error');
    }
});

stopBtn.addEventListener('click', async () => {
    await apiCall('/api/stop', 'POST');
    addLog('Stopping data acquisition...', 'info');
    systemStatus.streaming = false;
    updateButtonStates();
});

logBtn.addEventListener('click', async () => {
    if (!isLogging) {
        const sessionName = prompt('Enter session name:', 'track_session') || 'session';
        await apiCall('/api/logging/start', 'POST', { session_name: sessionName });
        addLog(`Logging started: ${sessionName}`, 'success');
        isLogging = true;
        logBtn.textContent = 'Stop Logging';
        logBtn.classList.remove('btn-secondary');
        logBtn.classList.add('btn-danger');
    } else {
        await apiCall('/api/logging/stop', 'POST');
        addLog('Logging stopped', 'info');
        isLogging = false;
        logBtn.textContent = 'Start Logging';
        logBtn.classList.remove('btn-danger');
        logBtn.classList.add('btn-secondary');
    }
});

// Update functions
function updateGauges(data) {
    // Coolant temperature
    const coolantElem = document.getElementById('coolantTemp');
    if (data.coolant_temp !== null && data.coolant_temp !== undefined) {
        coolantElem.textContent = data.coolant_temp.toFixed(1);
        updateGaugeAlert(coolantElem.parentElement, data.coolant_temp, 90, 100);
    }
    
    // Oil temperature
    const oilTempElem = document.getElementById('oilTemp');
    if (data.oil_temp !== null && data.oil_temp !== undefined) {
        oilTempElem.textContent = data.oil_temp.toFixed(1);
        updateGaugeAlert(oilTempElem.parentElement, data.oil_temp, 110, 120);
    }
    
    // Oil pressure
    const oilPressureElem = document.getElementById('oilPressure');
    if (data.oil_pressure !== null && data.oil_pressure !== undefined) {
        oilPressureElem.textContent = data.oil_pressure.toFixed(1);
    }
    
    // Throttle position
    const throttleElem = document.getElementById('throttle');
    if (data.throttle_position !== null && data.throttle_position !== undefined) {
        throttleElem.textContent = data.throttle_position.toFixed(0);
    }
}

function updateGaugeAlert(gaugeCard, value, warningThreshold, dangerThreshold) {
    gaugeCard.classList.remove('warning', 'danger');
    if (value >= dangerThreshold) {
        gaugeCard.classList.add('danger');
    } else if (value >= warningThreshold) {
        gaugeCard.classList.add('warning');
    }
}

function updateUI() {
    // Update status indicator
    if (systemStatus.connected) {
        statusDot.classList.add('connected');
        statusText.textContent = systemStatus.streaming ? 'Streaming' : 'Connected';
        connectBtn.textContent = 'Disconnect';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
        connectBtn.textContent = 'Connect';
    }
    
    updateButtonStates();
}

function updateButtonStates() {
    startBtn.disabled = !systemStatus.connected || systemStatus.streaming;
    stopBtn.disabled = !systemStatus.streaming;
    logBtn.disabled = !systemStatus.connected;
}

function addLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const logMsg = document.createElement('div');
    logMsg.className = `log-entry ${type}`;
    logMsg.innerHTML = `<span class="log-timestamp">${timestamp}</span><span class="log-message">${message}</span>`;
    logMessages.appendChild(logMsg);
    logMessages.scrollTop = logMessages.scrollHeight;
}

// API helper
async function apiCall(endpoint, method, data = null) {
    try {
        const response = await fetch(endpoint, {
            method: method,
            headers: data ? { 'Content-Type': 'application/json' } : {},
            body: data ? JSON.stringify(data) : null
        });
        
        const result = await response.json();
        
        // Handle success
        if (result.success) {
            if (endpoint.includes('connect')) {
                systemStatus.connected = true;
                updateUI();
            } else if (endpoint.includes('disconnect')) {
                systemStatus.connected = false;
                systemStatus.streaming = false;
                updateUI();
            }
        } else {
            // Handle API error responses (400, etc.)
            if (result.message) {
                addLog(result.message, 'error');
            }
        }
        
        return result;
    } catch (error) {
        addLog(`API Error: ${error.message}`, 'error');
        console.error(error);
        return { success: false, message: error.message };
    }
}