// WebSocket connection
const socket = io();

// DOM elements
const connectBtn = document.getElementById('connectBtn');
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
    addLog('Dashboard loaded', 'info');
    updateButtonStates();
});

// Socket events
socket.on('connect', () => {
    addLog('WebSocket connected', 'success');
});

socket.on('disconnect', () => {
    addLog('WebSocket disconnected', 'error');
});

socket.on('status', (status) => {
    systemStatus = status;
    updateUI();
});

socket.on('sensor_data', (data) => {
    updateGauges(data);
    updateCharts(data);
});

// Button handlers
connectBtn.addEventListener('click', async () => {
    if (!systemStatus.connected) {
        await apiCall('/api/connect', 'POST');
        addLog('Connecting to serial port...', 'info');
    } else {
        await apiCall('/api/disconnect', 'POST');
        addLog('Disconnecting...', 'info');
    }
});

startBtn.addEventListener('click', async () => {
    await apiCall('/api/start', 'POST');
    addLog('Starting data acquisition...', 'success');
    systemStatus.streaming = true;
    updateButtonStates();
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
    if (data.coolant_temp !== null) {
        coolantElem.textContent = data.coolant_temp.toFixed(1);
        updateGaugeAlert(coolantElem.parentElement, data.coolant_temp, 90, 100);
    }
    
    // Oil temperature
    const oilTempElem = document.getElementById('oilTemp');
    if (data.oil_temp !== null) {
        oilTempElem.textContent = data.oil_temp.toFixed(1);
        updateGaugeAlert(oilTempElem.parentElement, data.oil_temp, 110, 120);
    }
    
    // Oil pressure
    const oilPressureElem = document.getElementById('oilPressure');
    if (data.oil_pressure !== null) {
        oilPressureElem.textContent = data.oil_pressure.toFixed(1);
    }
    
    // Throttle position
    const throttleElem = document.getElementById('throttle');
    if (data.throttle_position !== null) {
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
    logMsg.className = `log-message ${type}`;
    logMsg.textContent = `[${timestamp}] ${message}`;
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
        
        if (result.success) {
            if (endpoint.includes('connect')) {
                systemStatus.connected = true;
                updateUI();
            } else if (endpoint.includes('disconnect')) {
                systemStatus.connected = false;
                systemStatus.streaming = false;
                updateUI();
            }
        }
        
        return result;
    } catch (error) {
        addLog(`API Error: ${error.message}`, 'error');
        console.error(error);
    }
}