# bpw4 monitoring solution (stock ecu / na8c)


![System Architecture](docs/architecture.png)



A complete data acquisition system for monitoring engine parameters in real-time:
- **Coolant Temperature** - NTC thermistor sensor
- **Oil Temperature** - NTC thermistor sensor  
- **Oil Pressure** - 0-150 PSI pressure sender
- **Throttle Position** - Variable resistor (potentiometer)

**Sample Rate:** 10 Hz (configurable)  
**Data Output:** CSV logging + real-time web dashboard  
**Communication:** Serial USB (115200 baud)

## System Architecture

```
┌──────────────┐       USB Serial      ┌──────────────┐      WebSocket     ┌──────────────┐
│   Arduino    │ ───────────────────► │   Python     │ ───────────────► │   Browser    │
│   Uno/Nano   │    115200 baud       │   Backend    │   Socket.IO      │   Dashboard  │
│              │                       │  (Flask)     │                   │              │
│  - ADC Read  │                       │              │                   │  - Gauges    │
│  - Filtering │                       │  - Parsing   │                   │  - Charts    │
│  - CSV Out   │                       │  - Logging   │                   │  - Logging   │
└──────────────┘                       └──────────────┘                   └──────────────┘
      ↑                                                                            
  Sensors:                                                                        
  - Coolant Temp (A0)                                                             
  - Oil Temp (A1)                                                                 
  - Oil Pressure (A2)                                                             
  - Throttle (A3)                                                                 
```

## features

### arduino
-  Object-oriented sensor classes
-  10-sample averaging filter for noise reduction
-  Calibration lookup tables with linear interpolation
-  Bounds checking and error handling (NAN on invalid readings)
-  CSV serial output format
-  Configurable sample rate

### python/flask
-  Auto-detection of Arduino serial port
-  Threaded serial communication (non-blocking)
-  Automatic reconnection on connection loss
-  Real-time WebSocket streaming (Socket.IO)
-  Session-based CSV logging with timestamps
-  RESTful API for control

### web dashboard
- Real-time gauge displays
- Live Chart.js graphs for trends
- Connect/disconnect control
- Start/stop data acquisition
- Session logging with custom names
- System log messages
- Visual alerts for critical thresholds


### req components
- **arduino Uno/Nano** - ATmega328P (5V)
- **temperature sensors** - NTC Thermistors (e.g., 2.5kΩ @ 20°C)
- **pressure Sensor** - VDO 0-150 PSI sender (0.5-4.5V)
- **throttle position Sensor** - Variable resistor from TPS
- **resistors** - Pull-up/down and voltage dividers as needed
- **capacitors** - 0.1µF ceramic for ADC filtering
- **breadboard/PCB** - For prototyping/production

### wiring 

```
Arduino Pin Assignments:
┌─────────────────────────────────────┐
│ A0 → Coolant Temp Sensor            │
│ A1 → Oil Temp Sensor                │
│ A2 → Oil Pressure Sensor            │
│ A3 → Throttle Position Sensor       │
│ 5V → Sensor Power                   │
│ GND → Sensor Ground                 │
│ USB → Computer/Raspberry Pi         │
└─────────────────────────────────────┘

Sensor Connections:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Temperature (NTC Thermistor):
  5V ─┬─ 2.2kΩ ─┬─ Thermistor ─ GND
      │         └─ ADC Pin (A0/A1)
      └─ 0.1µF capacitor ─ GND

Pressure Sender:
  5V ─ Sensor+ (signal) ─ ADC Pin (A2)
  GND ─ Sensor-

Throttle Position:
  5V ─ TPS+ (high)
  Signal ─ ADC Pin (A3)
  GND ─ TPS- (low)
```



### arduino firmware

```bash
# Install PlatformIO (recommended) or Arduino IDE
pip install platformio

# Upload firmware
cd firmware
pio run --target upload

# Monitor serial output
pio device monitor
```

**Or using Arduino IDE:**
1. Open `firmware/src/main.cpp`
2. Select board: Tools → Board → Arduino Uno
3. Select port: Tools → Port → (your Arduino port)
4. Upload: Sketch → Upload

### 2. Python Backend

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Run server
python app.py
```

Backend will start on `http://localhost:5000`

### 3. Access Dashboard

Open browser and navigate to:
```
http://localhost:5000
```


### init data acquisition

1. **Connect Arduino** - Plug Arduino via USB
2. **Start Backend** - Run `python backend/app.py`
3. **Open Dashboard** - Navigate to http://localhost:5000
4. **Click "Connect"** - Auto-detects Arduino port
5. **Click "Start"** - Begin streaming data at 10Hz
6. **Click "Start Logging"** - Save data to CSV (optional)

### Data Logging

Logged data is saved to `data/logs/` with format:
```
session_name_YYYYMMDD_HHMMSS.csv
```

CSV Format:
```csv
timestamp,coolant_temp,oil_temp,oil_pressure,throttle_position
0.100,85.4,92.1,45.2,12.5
0.200,85.5,92.3,45.0,15.8
...
```


5. **Update** `firmware/src/calibration.h`:
   ```cpp
   const TempPoint COOLANT_TEMP_CURVE[] = {
       {0.8, 0.0},    // Your measured voltage at 0°C
       {1.5, 20.0},   // Your measured voltage at 20°C
       {2.3, 60.0},   // Your measured voltage at 60°C
       {3.2, 100.0}   // Your measured voltage at 100°C
   };
   ```


### sample rate

Edit `firmware/src/config.h`:
```cpp
#define SAMPLE_RATE_HZ 10  // Change to 5, 10, 20, etc.
```

### thresholds

Edit `backend/config.py`:
```python
ALERT_COOLANT_TEMP = 100.0   # °C
ALERT_OIL_TEMP = 120.0        # °C
ALERT_OIL_PRESSURE_MIN = 20.0 # PSI
```

### serial Port manual Override

If auto-detection fails, set manually in `backend/config.py`:
```python
SERIAL_PORT = '/dev/ttyUSB0'  # Linux
# SERIAL_PORT = 'COM3'        # Windows
# SERIAL_PORT = '/dev/cu.usbserial-*'  # macOS
```



```
miatainterfacer/
├── firmware/               # Arduino C++ code
│   ├── src/
│   │   ├── main.cpp       # Main program loop
│   │   ├── sensors.h      # Sensor class definitions
│   │   ├── sensors.cpp    # Sensor implementations
│   │   ├── config.h       # Pin & system config
│   │   └── calibration.h  # Sensor calibration curves
│   └── platformio.ini     # PlatformIO config
│
├── backend/               # Python Flask server
│   ├── app.py            # Main Flask application
│   ├── serial_handler.py # Serial communication & threading
│   ├── data_logger.py    # CSV logging functionality
│   ├── config.py         # Backend configuration
│   └── requirements.txt  # Python dependencies
│
├── frontend/             # Web dashboard
│   ├── templates/
│   │   └── index.html   # Dashboard HTML
│   └── static/
│       ├── css/
│       │   └── style.css      # Dashboard styling
│       └── js/
│           ├── dashboard.js   # UI logic & controls
│           └── chart.js       # Chart.js graphs
│
├── data/
│   └── logs/            # CSV log files (created at runtime)
│
├── docs/                # Documentation & images
│
└── tests/              # Unit tests
```



### install
**power** - USB power from 12V→5V USB adapter (cig lighter will do)