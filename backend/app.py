"""main flask application with SocketIO"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet

from config import Config
from serial_handler import SerialHandler, SensorData
from data_logger import DataLogger

# Monkey patch for eventlet
eventlet.monkey_patch()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static',
            static_url_path='/static')
app.config.from_object(Config)

# Enable CORS and SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize handlers
serial_handler = SerialHandler(Config.SERIAL_PORT, Config.SERIAL_BAUD)
data_logger = DataLogger(Config.LOG_DIRECTORY)

# Global state
system_status = {
    'connected': False,
    'streaming': False,
    'logging': False
}

def broadcast_data(data: SensorData):
    """Broadcast sensor data to all connected clients"""
    socketio.emit('sensor_data', {
        'timestamp': data.timestamp,
        'coolant_temp': data.coolant_temp,
        'oil_temp': data.oil_temp,
        'oil_pressure': data.oil_pressure,
        'throttle_position': data.throttle_position
    })
    
    # Log if enabled
    if system_status['logging']:
        data_logger.log_data(data)

# Routes
@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify(system_status)

@app.route('/api/connect', methods=['POST'])
def connect_serial():
    """Connect to serial port"""
    if serial_handler.connect():
        system_status['connected'] = True
        return jsonify({'success': True, 'message': 'Connected'})
    return jsonify({'success': False, 'message': 'Connection failed'}), 500

@app.route('/api/disconnect', methods=['POST'])
def disconnect_serial():
    """Disconnect from serial port"""
    serial_handler.disconnect()
    system_status['connected'] = False
    system_status['streaming'] = False
    return jsonify({'success': True, 'message': 'Disconnected'})

@app.route('/api/start', methods=['POST'])
def start_streaming():
    """Start data streaming"""
    if not system_status['connected']:
        return jsonify({'success': False, 'message': 'Not connected'}), 400
    
    serial_handler.start_streaming(broadcast_data)
    system_status['streaming'] = True
    return jsonify({'success': True, 'message': 'Streaming started'})

@app.route('/api/stop', methods=['POST'])
def stop_streaming():
    """Stop data streaming"""
    serial_handler.stop_streaming()
    system_status['streaming'] = False
    return jsonify({'success': True, 'message': 'Streaming stopped'})

@app.route('/api/logging/start', methods=['POST'])
def start_logging():
    """Start data logging"""
    data = request.get_json() or {}
    session_name = data.get('session_name', 'session')
    
    data_logger.start_logging(session_name)
    system_status['logging'] = True
    return jsonify({'success': True, 'message': 'Logging started'})

@app.route('/api/logging/stop', methods=['POST'])
def stop_logging():
    """Stop data logging"""
    data_logger.stop_logging()
    system_status['logging'] = False
    return jsonify({'success': True, 'message': 'Logging stopped'})

# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print('Client connected')
    emit('status', system_status)

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print('Client disconnected')

if __name__ == '__main__':
    print("=" * 50)
    print("MX5 Data Acquisition System - Web Dashboard")
    print("=" * 50)
    print(f"Serial Port: {Config.SERIAL_PORT}")
    print(f"Dashboard: http://localhost:5000")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=Config.DEBUG)