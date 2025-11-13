"""CSV data logging functionality"""

import csv
import os
from datetime import datetime
from pathlib import Path

class DataLogger:
    """csv log"""
    
    def __init__(self, log_directory: str = '../data/logs'):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.current_file = None
        self.csv_writer = None
        self.is_logging = False
        
    def start_logging(self, session_name: str = None):
        """start new logging session"""
        if self.is_logging:
            return
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{session_name or 'session'}_{timestamp}.csv"
        filepath = self.log_directory / filename
        
        # Open file and create CSV writer
        self.current_file = open(filepath, 'w', newline='')
        self.csv_writer = csv.writer(self.current_file)
        
        # Write header
        self.csv_writer.writerow([
            'timestamp', 'coolant_temp', 'oil_temp', 
            'oil_pressure', 'throttle_position'
        ])
        
        self.is_logging = True
        print(f"✓ logging to: {filepath}")
        
    def stop_logging(self):
        """stop logging and close file"""
        if not self.is_logging:
            return
        
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.csv_writer = None
        
        self.is_logging = False
        print("✓ logging stopped")
    
    def log_data(self, data):
        """Write data to CSV"""
        if not self.is_logging or not self.csv_writer:
            return
        
        self.csv_writer.writerow([
            data.timestamp,
            data.coolant_temp,
            data.oil_temp,
            data.oil_pressure,
            data.throttle_position
        ])
        
        # flush periodically to ensure data is written
        if int(data.timestamp * 10) % 10 == 0:  
            self.current_file.flush()