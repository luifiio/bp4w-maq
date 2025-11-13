"""
Demo mode for MX5 DAQ System
Simulates sensor data for testing the web dashboard without Arduino
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet
import random
import time
from threading import Thread, Event

# Monkey patch for eventlet
eventlet.monkey_patch()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static',
            static_url_path='/static')
app.config['SECRET_KEY'] = 'demo-secret-key'

# Enable CORS and SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Demo state
demo_state = {
    'connected': False,
    'streaming': False,
    'is_running': Event()
}

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
    
    # Warm-up phase (first 30 seconds)
    warmup_progress = min(sensor_state['timestamp'] / 30.0, 1.0)
    
    # Coolant temp: slowly rises to operating temp (85-95°C)
    target_coolant = 85 + random.uniform(-2, 5)
    sensor_state['coolant_temp'] += (target_coolant - sensor_state['coolant_temp']) * 0.02
    sensor_state['coolant_temp'] += random.uniform(-0.5, 0.5)  # Small fluctuations
    
    # Oil temp: follows coolant but slightly higher (90-110°C)
    target_oil = sensor_state['coolant_temp'] + 5 + random.uniform(0, 10)
    sensor_state['oil_temp'] += (target_oil - sensor_state['oil_temp']) * 0.015
    sensor_state['oil_temp'] += random.uniform(-0.3, 0.3)
    
    # Oil pressure: depends on throttle (idle: 15-25 PSI, cruise: 40-60 PSI)
    if sensor_state['throttle'] < 10:
        target_pressure = 15 + warmup_progress * 5  # Low at idle
    else:
        target_pressure = 35 + (sensor_state['throttle'] / 100.0) * 25
    
    sensor_state['oil_pressure'] += (target_pressure - sensor_state['oil_pressure']) * 0.1
    sensor_state['oil_pressure'] += random.uniform(-1, 1)
    sensor_state['oil_pressure'] = max(5, sensor_state['oil_pressure'])  # Never below 5 PSI
    
    # Throttle: simulate driving pattern
    throttle_change = random.choice([
        random.uniform(-5, -2),   # Deceleration
        random.uniform(-1, 1),    # Steady
        random.uniform(2, 8)      # Acceleration
    ])
    sensor_state['throttle'] += throttle_change
    sensor_state['throttle'] = max(0, min(100, sensor_state['throttle']))  # Clamp 0-100

def broadcast_demo_data():
    """Background thread to broadcast simulated data"""
    while demo_state['is_running'].is_set():
        sensor_state['timestamp'] += 0.1  # 10 Hz
        simulate_sensor_data()
        
        # Broadcast to all connected clients
        socketio.emit('sensor_data', {
            'timestamp': sensor_state['timestamp'],
            'coolant_temp': round(sensor_state['coolant_temp'], 1),
            'oil_temp': round(sensor_state['oil_temp'], 1),
            'oil_pressure': round(sensor_state['oil_pressure'], 1),
            'throttle_position': round(sensor_state['throttle'], 1)
        })
        
        socketio.sleep(0.1)  # 10 Hz update rate

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
    demo_state['is_running'].clear()
    return jsonify({'success': True, 'message': 'Demo mode disconnected'})

@app.route('/api/start', methods=['POST'])
def start_demo():
    """Start demo data streaming"""
    if not demo_state['connected']:
        return jsonify({'success': False, 'message': 'Not connected'}), 400
    
    demo_state['streaming'] = True
    demo_state['is_running'].set()
    
    # Start background thread
    thread = Thread(target=broadcast_demo_data, daemon=True)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Demo streaming started'})

@app.route('/api/stop', methods=['POST'])
def stop_demo():
    """Stop demo data streaming"""
    demo_state['is_running'].clear()
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
    emit('status', demo_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('[OK] Client disconnected from demo')

if __name__ == '__main__':
    print("=" * 60)
    print("   MX5 DAQ SYSTEM - DEMO MODE")
    print("=" * 60)
    print("")
    print("  Running without Arduino - Simulated sensor data")
    print("")
    print("  Dashboard: http://localhost:5000")
    print("")
    print("  Instructions:")
    print("    1. Open http://localhost:5000 in your browser")
    print("    2. Click 'Connect' to start demo mode")
    print("    3. Click 'Start' to see simulated sensor data")
    print("")
    print("=" * 60)
    print("")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
