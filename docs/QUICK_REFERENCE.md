# Quick Reference Guide

## 🚀 Quick Start (1-2-3)

```bash
# 1. Upload firmware to Arduino
cd firmware && pio run --target upload

# 2. Start web server
./start.sh

# 3. Open browser
http://localhost:5000
```

## 📌 Pin Assignments

| Pin | Sensor | Range | Notes |
|-----|--------|-------|-------|
| A0 | Coolant Temp | 0-5V | NTC thermistor |
| A1 | Oil Temp | 0-5V | NTC thermistor |
| A2 | Oil Pressure | 0.5-4.5V | 0-150 PSI sender |
| A3 | Throttle Position | 0.5-4.5V | TPS potentiometer |

## ⚙️ Configuration Quick Changes

### Change Sample Rate
File: `firmware/src/config.h`
```cpp
#define SAMPLE_RATE_HZ 20  // Change to 5, 10, 20, etc.
```

### Change Serial Port (Manual)
File: `backend/config.py`
```python
SERIAL_PORT = '/dev/ttyUSB0'  # Linux
SERIAL_PORT = 'COM3'          # Windows
SERIAL_PORT = '/dev/cu.usbserial-*'  # macOS
```

### Change Alert Thresholds
File: `backend/config.py`
```python
ALERT_COOLANT_TEMP = 95.0      # °C
ALERT_OIL_TEMP = 120.0         # °C
ALERT_OIL_PRESSURE_MIN = 15.0  # PSI
```

## 🔧 Common Commands

### Arduino Development
```bash
# Compile only
pio run

# Upload to Arduino
pio run --target upload

# Serial monitor
pio device monitor

# Clean build
pio run --target clean
```

### Python Backend
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run server (development)
python backend/app.py

# Run with auto-reload
FLASK_ENV=development python backend/app.py
```

### Calibration
```bash
# Run calibration wizard
python tools/calibrate.py
```

## 📊 Data Format

### Serial Output (Arduino → Python)
```csv
timestamp_ms,coolant_temp,oil_temp,oil_pressure,throttle
1000,85.5,92.3,45.2,12.5
1100,85.6,92.4,45.1,13.2
```

### CSV Log Files
Location: `data/logs/session_YYYYMMDD_HHMMSS.csv`

Format: Same as serial output with header row

### WebSocket Messages (Python → Browser)
```json
{
  "timestamp": 1.234,
  "coolant_temp": 85.5,
  "oil_temp": 92.3,
  "oil_pressure": 45.2,
  "throttle_position": 12.5
}
```

## 🐛 Troubleshooting Checklist

### Arduino Not Detected
- [ ] USB cable plugged in?
- [ ] Arduino powered (red LED on)?
- [ ] Correct drivers installed?
- [ ] Check available ports: `pio device list`
- [ ] Try different USB port
- [ ] Manual override in `config.py`

### No Data Streaming
- [ ] Arduino connected?
- [ ] Clicked "Connect" button?
- [ ] Clicked "Start" button?
- [ ] Check browser console (F12)
- [ ] Verify baud rate: 115200
- [ ] Test serial monitor: `pio device monitor`

### Invalid Readings (NAN)
- [ ] Check sensor wiring
- [ ] Measure voltage with multimeter (0-5V?)
- [ ] Verify calibration curves
- [ ] Check for loose connections
- [ ] Test with known voltage source

### Connection Keeps Dropping
- [ ] USB cable quality (try different cable)
- [ ] Cable length (max ~3m)
- [ ] EMI from car electrical system?
- [ ] Arduino power supply stable?
- [ ] Check Python console for errors

### Dashboard Not Loading
- [ ] Flask server running?
- [ ] Correct URL: http://localhost:5000
- [ ] Firewall blocking port 5000?
- [ ] Try http://127.0.0.1:5000
- [ ] Check backend console for errors

## 📏 Typical Readings (1998 MX5)

### Normal Operating Conditions
| Parameter | Normal Range | Warning | Critical |
|-----------|--------------|---------|----------|
| Coolant Temp | 80-95°C | 95-100°C | >100°C |
| Oil Temp | 85-110°C | 110-120°C | >120°C |
| Oil Pressure (idle) | 10-20 PSI | <10 PSI | <5 PSI |
| Oil Pressure (cruise) | 40-60 PSI | - | - |
| Throttle | 0-100% | - | - |

### Cold Start
- Coolant: 15-25°C (ambient)
- Oil: 15-25°C (ambient)
- Pressure: 30-40 PSI (cold oil)

### Hot Track Day
- Coolant: 90-95°C
- Oil: 100-115°C
- Pressure: 35-50 PSI (hot, high RPM)

## 🛠️ Hardware Tips

### Signal Noise Reduction
1. Add 0.1µF capacitor between ADC pin and GND
2. Keep sensor wires away from ignition wires
3. Use shielded cable for long runs
4. Twist sensor wires together
5. Increase `NUM_SAMPLES` in firmware

### Voltage Division (if sensor > 5V)
```
Vin ──┬── R1 ──┬── ADC Pin
      │        │
     Sensor   R2
             GND

Vout = Vin × R2 / (R1 + R2)

Example: 12V → 5V
  R1 = 7kΩ, R2 = 5kΩ
  Vout = 12 × 5/(7+5) = 5V
```

### Power Supply
- Arduino: USB 5V (500mA max)
- Sensors: Parasitic power from Arduino 5V pin
- Total current: <100mA (plenty of headroom)
- Car install: 12V→5V USB adapter (2A recommended)

## 🎯 Performance Specs

| Metric | Value | Notes |
|--------|-------|-------|
| Sample Rate | 10 Hz | Configurable (5-100 Hz) |
| ADC Resolution | 10-bit (1024 levels) | 0.0049V per step |
| Voltage Accuracy | ±0.01V | With 10-sample avg |
| Latency | ~100ms | Sensor → Dashboard |
| Log File Size | ~15 KB/min | 4 sensors @ 10Hz |
| Data Retention | Unlimited | CSV files |
| WebSocket Overhead | <5 KB/s | Minimal bandwidth |

## 📱 Access from Phone/Tablet

### Same Network
Find computer's IP address:
```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

Access from phone: `http://192.168.1.xxx:5000`

### In-Car Setup
1. Connect laptop to phone hotspot
2. Note laptop IP address
3. Access from phone browser
4. Pin to home screen for quick access

## 🔒 Safety Reminders

- ⚠️ **NOT a safety-critical system** - For data logging only
- ⚠️ **Do not rely on readings while driving** - Keep eyes on road
- ⚠️ **Secure all wiring** - Prevent interference with pedals/steering
- ⚠️ **Test thoroughly** before track use
- ⚠️ **Always have backup gauges** - Don't remove OEM sensors

## 📚 Additional Resources

### Documentation
- [README.md](../README.md) - Full documentation
- [IMPROVEMENTS.md](../IMPROVEMENTS.md) - Change summary
- [architecture.md](architecture.md) - Technical details

### External Links
- Arduino Reference: https://www.arduino.cc/reference
- Flask Documentation: https://flask.palletsprojects.com/
- Chart.js: https://www.chartjs.org/
- Socket.IO: https://socket.io/

### MX5-Specific
- Miata.net Forums: https://forum.miata.net/
- MX5 Service Manual (for sensor specs)
- OBD-II standards for pressure/temp ranges

---

**Need Help?** Check the troubleshooting section in README.md or open an issue on GitHub.

**Found a Bug?** Please report it with:
- Description of problem
- Steps to reproduce
- Console/serial output
- Arduino/Python versions
