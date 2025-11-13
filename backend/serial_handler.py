"""serial communication"""

import serial
import time
import json
from threading import Thread, Event
from typing import Optional, Callable
from dataclasses import dataclass, asdict

@dataclass
class SensorData:
    """sensor reading data structure"""
    timestamp: float
    coolant_temp: Optional[float] = None
    oil_temp: Optional[float] = None
    oil_pressure: Optional[float] = None
    throttle_position: Optional[float] = None
    
    def to_json(self):
        return json.dumps(asdict(self))

class SerialHandler:
    """ serial connection and data streaming"""
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[serial.Serial] = None
        self.is_running = Event()
        self.thread: Optional[Thread] = None
        self.data_callback: Optional[Callable] = None
        
    def connect(self) -> bool:
        """ serial connection"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            time.sleep(2)  # Arduino reset delay
            print(f"[OK] Connected to {self.port}")
            return True
        except serial.SerialException as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def disconnect(self):
        """close serial connection"""
        self.stop_streaming()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("[OK] Disconnected")
    
    def start_streaming(self, callback: Callable[[SensorData], None]):
        """start streaming data in background thread"""
        if self.is_running.is_set():
            return
        
        self.data_callback = callback
        self.is_running.set()
        self.thread = Thread(target=self._stream_loop, daemon=True)
        self.thread.start()
        print("[OK] Streaming started")
    
    def stop_streaming(self):
        """stop streaming data"""
        if self.is_running.is_set():
            self.is_running.clear()
            if self.thread:
                self.thread.join(timeout=2)
            print("[OK] Streaming stopped")
    
    def _stream_loop(self):
        """Background thread for reading serial data"""
        consecutive_errors = 0
        max_errors = 5
        
        while self.is_running.is_set():
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    if self.serial_conn.in_waiting:
                        line = self.serial_conn.readline().decode('utf-8').strip()
                        
                        if line and not line.startswith('MX5'):  # Skip headers
                            data = self._parse_line(line)
                            if data and self.data_callback:
                                self.data_callback(data)
                                consecutive_errors = 0  # Reset error count on success
                else:
                    # Connection lost, attempt reconnect
                    print("[WARNING] Connection lost, attempting reconnection...")
                    consecutive_errors += 1
                    if consecutive_errors < max_errors:
                        time.sleep(2)
                        if self.connect():
                            print("[OK] Reconnected successfully")
                            consecutive_errors = 0
                    else:
                        print("[ERROR] Max reconnection attempts reached")
                        self.is_running.clear()
                            
            except (UnicodeDecodeError, ValueError) as e:
                print(f"[WARNING] Data parsing error: {e}")
                time.sleep(0.1)
            except serial.SerialException as e:
                print(f"[ERROR] Serial error: {e}")
                consecutive_errors += 1
                if consecutive_errors < max_errors:
                    time.sleep(2)
                    try:
                        if self.connect():
                            print("[OK] Reconnected after error")
                            consecutive_errors = 0
                    except:
                        pass
                else:
                    print("[ERROR] Too many errors, stopping stream")
                    self.is_running.clear()
    
    def _parse_line(self, line: str) -> Optional[SensorData]:
        """Parse CSV line into SensorData"""
        try:
            parts = line.split(',')
            if len(parts) < 2:
                return None
            
            # Parse based on number of fields
            return SensorData(
                timestamp=float(parts[0]) / 1000.0,  # ms to seconds
                coolant_temp=float(parts[1]) if len(parts) > 1 else None,
                oil_temp=float(parts[2]) if len(parts) > 2 else None,
                oil_pressure=float(parts[3]) if len(parts) > 3 else None,
                throttle_position=float(parts[4]) if len(parts) > 4 else None
            )
        except (ValueError, IndexError):
            return None