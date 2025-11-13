"""config"""

import os
import serial.tools.list_ports

class Config:
    # flask 
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # serial - auto-detect Arduino port
    @staticmethod
    def find_arduino_port():
        """Auto-detect Arduino serial port"""
        ports = serial.tools.list_ports.comports()
        
        # Look for Arduino identifiers
        for port in ports:
            # Common Arduino USB identifiers
            if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'usb serial']):
                return port.device
            # Check manufacturer
            if port.manufacturer and 'arduino' in port.manufacturer.lower():
                return port.device
        
        # Fallback to first available port
        if ports:
            print(f"Warning: Arduino not auto-detected, using {ports[0].device}")
            return ports[0].device
        
        return None
    
    SERIAL_PORT = os.environ.get('SERIAL_PORT') or find_arduino_port.__func__()
    SERIAL_BAUD = 115200
    SERIAL_TIMEOUT = 1.0
    
    # data log
    LOG_DIRECTORY = '../data/logs'
    AUTO_LOG = True  
    
    # sensor configuration
    SAMPLE_RATE_HZ = 10
    
    # alert thresholds
    ALERT_COOLANT_TEMP = 100.0  # °C
    ALERT_OIL_TEMP = 120.0       # °C
    ALERT_OIL_PRESSURE_MIN = 20.0  # PSI
    
    # webscket 
    PING_INTERVAL = 25
    PING_TIMEOUT = 60