# Data Flow Architecture

## High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          MX5 DAQ SYSTEM                             │
└─────────────────────────────────────────────────────────────────────┘

    SENSORS          →    ARDUINO    →    PYTHON    →    WEB BROWSER
                                                    
 ┌──────────┐         ┌───────────┐    ┌──────────┐    ┌────────────┐
 │ Coolant  │─A0─────▶│           │    │          │    │  Gauges    │
 │   Temp   │         │  ADC      │    │  Flask   │    │            │
 └──────────┘         │  10-bit   │    │  Server  │    │  Real-time │
                      │  0-1023   │    │          │    │   Charts   │
 ┌──────────┐         │           │    │          │    │            │
 │   Oil    │─A1─────▶│  Signal   │USB │ Serial   │WS  │  Control   │
 │   Temp   │         │  Filter   │───▶│ Handler  │───▶│  Buttons   │
 └──────────┘         │  (10x)    │    │          │    │            │
                      │           │    │  CSV     │    │   Log      │
 ┌──────────┐         │  Calib.   │    │  Logger  │    │  Messages  │
 │   Oil    │─A2─────▶│  Lookup   │    │          │    │            │
 │ Pressure │         │  Tables   │    │          │    └────────────┘
 └──────────┘         │           │    └──────────┘         ▲
                      │  Serial   │         │               │
 ┌──────────┐         │  Output   │         ▼               │
 │ Throttle │─A3─────▶│  115200   │    ┌──────────┐         │
 │   (TPS)  │         │   baud    │    │   CSV    │    Socket.IO
 └──────────┘         │           │    │   Logs   │    (WebSocket)
                      └───────────┘    └──────────┘         │
    Analog            Arduino Uno      data/logs/       localhost:5000
   0-5V DC            ATmega328P       Timestamped
```

## Data Processing Pipeline

### 1. Sensor → ADC (Analog to Digital)
```
Voltage (0-5V) → Arduino ADC (10-bit) → Raw value (0-1023)

Example:
  2.5V → 512 (raw) → 2.5V (calculated)
```

### 2. Filtering (Noise Reduction)
```
Single reading → 10 samples → Average → Filtered voltage

Raw readings:  [510, 512, 511, 513, 509, 512, 511, 510, 512, 511]
Average:       511.1
Filtered:      2.499V
```

### 3. Calibration (Voltage → Real Units)
```
Voltage → Lookup Table Interpolation → Temperature/Pressure/Percent

Example (Temperature):
  Input:  2.3V
  Table:  2.0V=50°C, 2.5V=70°C
  Interp: 2.3V = 50 + (2.3-2.0)/(2.5-2.0) * (70-50)
        = 50 + 0.6 * 20 = 62°C
```

### 4. Serial Transmission (Arduino → Computer)
```
CSV Format:  timestamp_ms,coolant_temp,oil_temp,oil_pressure,throttle
Example:     1234,85.5,92.3,45.2,12.5

Baud Rate:   115200 bps
Frequency:   10 Hz (100ms intervals)
```

### 5. Python Processing
```
Serial port → Parse CSV → SensorData object → Broadcast

┌─────────────────────────────────────────┐
│  serial_handler.py (Background Thread)  │
│                                         │
│  1. Read line from serial              │
│  2. Parse CSV string                   │
│  3. Create SensorData object           │
│  4. Call broadcast callback            │
│  5. Loop (non-blocking)                │
└─────────────────────────────────────────┘
           │
           ├──▶ WebSocket broadcast to all clients
           │
           └──▶ CSV logger (if enabled)
```

### 6. Web Dashboard (Real-time Display)
```
WebSocket message → Update gauges → Update charts

Message:  {
  "timestamp": 1.234,
  "coolant_temp": 85.5,
  "oil_temp": 92.3,
  "oil_pressure": 45.2,
  "throttle_position": 12.5
}

Display:  [85.5°C]  ═════════▶  Chart updates
```

## Timing Diagram

```
Time:     0ms        100ms       200ms       300ms       400ms
          │          │           │           │           │
Arduino:  ├─Sample──▶├─Sample───▶├─Sample───▶├─Sample───▶├─Sample──▶
          │  10Hz    │   10Hz    │   10Hz    │   10Hz    │   10Hz
          │          │           │           │           │
Serial:   ├─TX───────┼─TX────────┼─TX────────┼─TX────────┼─TX───────▶
          │  CSV     │   CSV     │   CSV     │   CSV     │   CSV
          │          │           │           │           │
Python:   ├─Parse───▶├─Parse────▶├─Parse────▶├─Parse────▶├─Parse───▶
          │  Thread  │  Thread   │  Thread   │  Thread   │  Thread
          │          │           │           │           │
WebSocket:├─Broadcast├─Broadcast─├─Broadcast─├─Broadcast─├─Broadcast▶
          │  <1ms    │   <1ms    │   <1ms    │   <1ms    │   <1ms
          │          │           │           │           │
Browser:  ├─Update──▶├─Update───▶├─Update───▶├─Update───▶├─Update──▶
          │  Render  │  Render   │  Render   │  Render   │  Render

Total Latency: ~100ms (dominated by sample period)
```

## Error Handling Flow

```
Connection Error Detected
        │
        ▼
   Is it < 5 errors?
        │
   Yes ─┼─▶ Wait 2 seconds
        │         │
        │         ▼
        │    Attempt Reconnect
        │         │
        │    Success?
        │    │    │
        │   Yes  No
        │    │    │
        │    ▼    │
        │  Reset  │
        │  Counter│
        │    │    │
        └────┴────┘
             │
            Loop
             
        No
        │
        ▼
   Stop Streaming
   Show Error Message
```

## File Organization

```
miatainterfacer/
│
├── firmware/              ← ARDUINO CODE
│   ├── src/
│   │   ├── main.cpp           [Main loop, setup()]
│   │   ├── sensors.cpp        [Sensor classes]
│   │   ├── sensors.h          [Sensor interfaces]
│   │   ├── config.h           [Pin definitions]
│   │   └── calibration.h      [Lookup tables]
│   └── platformio.ini     [Build config]
│
├── backend/               ← PYTHON SERVER
│   ├── app.py                 [Flask routes]
│   ├── serial_handler.py      [USB serial]
│   ├── data_logger.py         [CSV writer]
│   ├── config.py              [Settings]
│   └── requirements.txt   [Dependencies]
│
├── frontend/              ← WEB INTERFACE
│   ├── templates/
│   │   └── index.html         [Dashboard HTML]
│   └── static/
│       ├── css/style.css      [Styling]
│       └── js/
│           ├── dashboard.js   [UI logic]
│           └── chart.js       [Graphs]
│
├── data/
│   └── logs/              ← CSV DATA FILES
│       └── session_*.csv
│
├── tools/
│   └── calibrate.py       ← CALIBRATION HELPER
│
├── docs/
│   └── architecture.md    [This file]
│
├── start.sh               ← STARTUP SCRIPT
└── README.md              ← DOCUMENTATION
```

## Communication Protocol

### Arduino → Python (Serial)
```
Format:   CSV (Comma-Separated Values)
Encoding: UTF-8
Newline:  \n (LF)
Baud:     115200

Header line:
  "timestamp_ms,coolant_temp_c"

Data lines:
  "1234,85.5\n"
  "1334,85.6\n"
  ...

Python ignores lines starting with "MX5" (headers)
```

### Python → Browser (WebSocket)
```
Protocol: Socket.IO (WebSocket wrapper)
Format:   JSON
Event:    'sensor_data'

Message:
{
  "timestamp": 1.234,
  "coolant_temp": 85.5,
  "oil_temp": 92.3,
  "oil_pressure": 45.2,
  "throttle_position": 12.5
}

Broadcast to all connected clients simultaneously
```

### Browser → Python (HTTP + WebSocket)
```
HTTP REST API:
  POST /api/connect       - Connect to serial
  POST /api/disconnect    - Disconnect
  POST /api/start         - Start streaming
  POST /api/stop          - Stop streaming
  POST /api/logging/start - Start CSV logging
  POST /api/logging/stop  - Stop CSV logging
  GET  /api/status        - Get system status

WebSocket Events:
  'connect'    - Client connected
  'disconnect' - Client disconnected
```

---

This architecture provides:
- **Low latency**: ~100ms total (sensor → display)
- **High reliability**: Automatic reconnection
- **Scalability**: Multiple browser clients supported
- **Data persistence**: CSV logging for analysis
- **Real-time feedback**: 10 Hz update rate
