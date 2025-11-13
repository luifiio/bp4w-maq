"""
Demo mode for MX5 DAQ System
Simulates sensor data for testing the web dashboard without Arduino
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
import eventlet
from threading import Event

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static',
            static_url_path='/static')
app.config['SECRET_KEY'] = 'demo-secret-key'

# Enable CORS with full permissions
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Initialize SocketIO with CORS
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=True,
                   async_mode='eventlet',
                   cors_credentials=False,
                   allow_upgrades=True)

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Demo state
demo_state = {
    'connected': False,
    'streaming': False,
    'logging': False
}

# Background thread control
is_running = Event()
broadcast_thread = None

# Simulated sensor values
sensor_state = {
    'coolant_temp': 20.0,  # Start at ambient
    'oil_temp': 20.0,
    'oil_pressure': 0.0,
    'throttle': 0.0,
    'timestamp': 0.0
}

def simulate_sensor_data():
    """Simulate realistic sensor data patterns"""
    import math
    
    t = sensor_state['timestamp']
    
    # Warm-up phase (first 30 seconds)
    warmup_progress = min(t / 30.0, 1.0)
    
    # Coolant temp: oscillates around operating temp with realistic variation
    # Base operating temp with sine wave for cooling cycles
    base_coolant = 88 + math.sin(t / 10.0) * 4  # 10 second cooling cycle, ±4°C
    sensor_state['coolant_temp'] += (base_coolant - sensor_state['coolant_temp']) * 0.05
    sensor_state['coolant_temp'] += random.uniform(-1.5, 1.5)  # Increased fluctuation
    sensor_state['coolant_temp'] = max(20, min(105, sensor_state['coolant_temp']))
    
    # Oil temp: follows coolant but lags and runs hotter
    # More dramatic oscillation showing heat buildup
    base_oil = sensor_state['coolant_temp'] + 8 + math.sin(t / 15.0) * 6
    sensor_state['oil_temp'] += (base_oil - sensor_state['oil_temp']) * 0.03
    sensor_state['oil_temp'] += random.uniform(-1.2, 1.2)
    sensor_state['oil_temp'] = max(20, min(125, sensor_state['oil_temp']))
    
    # Oil pressure: depends on throttle and temp (hotter = lower pressure)
    temp_factor = max(0.7, 1.0 - (sensor_state['oil_temp'] - 90) / 100.0)
    if sensor_state['throttle'] < 10:
        target_pressure = (15 + warmup_progress * 5) * temp_factor
    else:
        target_pressure = (35 + (sensor_state['throttle'] / 100.0) * 25) * temp_factor
    
    sensor_state['oil_pressure'] += (target_pressure - sensor_state['oil_pressure']) * 0.1
    sensor_state['oil_pressure'] += random.uniform(-2, 2)  # More variation
    sensor_state['oil_pressure'] = max(5, min(80, sensor_state['oil_pressure']))
    
    # Throttle: simulate realistic driving cycles
    # Mix of steady state, acceleration, and deceleration
    if random.random() < 0.3:  # 30% chance of significant change
        throttle_change = random.choice([
            random.uniform(-15, -8),   # Heavy braking
            random.uniform(-5, -2),    # Light deceleration
            random.uniform(5, 15)      # Acceleration
        ])
    else:
        throttle_change = random.uniform(-2, 2)  # Gentle variation
    
    sensor_state['throttle'] += throttle_change
    sensor_state['throttle'] = max(0, min(100, sensor_state['throttle']))  # Clamp 0-100

def broadcast_demo_data():
    """Background thread to broadcast simulated data"""
    print('[OK] Broadcast thread started')
    count = 0
    while is_running.is_set():
        sensor_state['timestamp'] += 0.1  # 10 Hz
        simulate_sensor_data()
        
        # Broadcast to all connected clients
        data = {
            'timestamp': sensor_state['timestamp'],
            'coolant_temp': round(sensor_state['coolant_temp'], 1),
            'oil_temp': round(sensor_state['oil_temp'], 1),
            'oil_pressure': round(sensor_state['oil_pressure'], 1),
            'throttle_position': round(sensor_state['throttle'], 1)
        }
        
        # Emit to all connected clients
        socketio.emit('sensor_data', data)
        
        # Debug output every 2 seconds
        count += 1
        if count % 20 == 0:
            print(f'[DEBUG] Emitting: coolant={data["coolant_temp"]}°C, oil={data["oil_temp"]}°C, pressure={data["oil_pressure"]}PSI, throttle={data["throttle_position"]}%')
        
        eventlet.sleep(0.1)  # 10 Hz update rate - using eventlet.sleep to allow WebSocket keepalive
    
    print('[OK] Broadcast thread stopped')

# Routes
@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify(demo_state)

@app.route('/api/connect', methods=['POST'])
def connect_demo():
    """Simulate connection"""
    demo_state['connected'] = True
    return jsonify({'success': True, 'message': 'Demo mode connected'})

@app.route('/api/disconnect', methods=['POST'])
def disconnect_demo():
    """Simulate disconnection"""
    demo_state['connected'] = False
    demo_state['streaming'] = False
    is_running.clear()
    return jsonify({'success': True, 'message': 'Demo mode disconnected'})

@app.route('/api/start', methods=['POST'])
def start_demo():
    """Start demo data streaming"""
    global broadcast_thread
    
    if not demo_state['connected']:
        print('[ERROR] Start requested but not connected')
        return jsonify({'success': False, 'message': 'Please connect first'}), 400
    
    if demo_state['streaming']:
        return jsonify({'success': True, 'message': 'Already streaming'})
    
    demo_state['streaming'] = True
    is_running.set()
    
    # Start background thread if not already running
    if broadcast_thread is None or not broadcast_thread.is_alive():
        broadcast_thread = socketio.start_background_task(broadcast_demo_data)
        print('[OK] Started demo data broadcast thread')
    
    return jsonify({'success': True, 'message': 'Demo streaming started'})

@app.route('/api/stop', methods=['POST'])
def stop_demo():
    """Stop demo data streaming"""
    is_running.clear()
    demo_state['streaming'] = False
    return jsonify({'success': True, 'message': 'Demo streaming stopped'})

@app.route('/api/logging/start', methods=['POST'])
def start_logging():
    """Simulate logging start"""
    return jsonify({'success': True, 'message': 'Demo logging (simulated)'})

@app.route('/api/logging/stop', methods=['POST'])
def stop_logging():
    """Simulate logging stop"""
    return jsonify({'success': True, 'message': 'Demo logging stopped (simulated)'})

# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('[OK] Client connected to demo')
    emit('status', {
        'connected': demo_state['connected'],
        'streaming': demo_state['streaming'],
        'logging': demo_state['logging']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('[OK] Client disconnected from demo')

if __name__ == '__main__':
    print("=" * 60)
    print("   MX5 DAQ SYSTEM - DEMO MODE")
    print("=" * 60)
    print()
    print("  Running without Arduino - Simulated sensor data")
    print()
    print("  Dashboard: http://localhost:8000")
    print()
    print("  Instructions:")
    print("    1. Open http://localhost:8000 in your browser")
    print("    2. Click 'Connect' to start demo mode")
    print("    3. Click 'Start' to see simulated sensor data")
    print()
    print("=" * 60)
    print()
    
    # Disable template caching for development
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    socketio.run(app, host='0.0.0.0', port=8000, debug=False)
