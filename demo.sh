#!/bin/bash
# Demo mode startup script - No Arduino required!

echo "================================================"
echo "   MX5 DAQ System - DEMO MODE"
echo "================================================"
echo ""
echo "Starting demo with simulated sensor data..."
echo "No Arduino connection required."
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check/create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies (if needed)..."
pip install -q -r backend/requirements.txt

echo ""
echo "================================================"
echo "Starting demo server..."
echo ""
echo "  Dashboard: http://localhost:5000"
echo ""
echo "  Instructions:"
echo "    1. Open the URL above in your browser"
echo "    2. Click 'Connect'"
echo "    3. Click 'Start' to see live simulated data"
echo ""
echo "  Press Ctrl+C to stop"
echo "================================================"
echo ""

# Start demo
cd backend
python3 demo.py
