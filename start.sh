#!/bin/bash
# Quick start script for MX5 DAQ System

echo "================================================"
echo "   MX5 Data Acquisition System - Startup"
echo "================================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "[OK] Python 3 found"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r backend/requirements.txt

# Check for Arduino connection
echo ""
echo "Checking for Arduino..."
python3 -c "
import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
if ports:
    print('[OK] Found serial ports:')
    for port in ports:
        print(f'  - {port.device}: {port.description}')
else:
    print('[WARNING] No serial ports detected. Connect Arduino and try again.')
"

echo ""
echo "================================================"
echo "Starting Flask server..."
echo "Dashboard will be available at:"
echo "  http://localhost:5000"
echo "================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask app
cd backend
python3 app.py
