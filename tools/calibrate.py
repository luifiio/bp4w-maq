"""
Sensor Calibration Helper Tool
Assists in creating calibration curves for temperature and pressure sensors
"""

import serial
import time
import sys

def find_arduino():
    """Find Arduino port automatically"""
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'usb serial']):
            return port.device
    
    if ports:
        return ports[0].device
    return None

def read_voltage(ser, pin, samples=50):
    """Read averaged voltage from specified pin"""
    values = []
    
    print(f"Reading {samples} samples from pin {pin}...")
    for i in range(samples):
        # In real implementation, you'd send command to Arduino
        # For now, read from serial stream
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line and ',' in line:
                parts = line.split(',')
                if len(parts) > 1:
                    try:
                        # Assuming format: timestamp,value
                        values.append(float(parts[1]))
                    except ValueError:
                        pass
        time.sleep(0.1)
    
    if values:
        avg = sum(values) / len(values)
        return avg
    return None

def calibrate_temperature():
    """Guide user through temperature sensor calibration"""
    print("\n" + "="*60)
    print("TEMPERATURE SENSOR CALIBRATION")
    print("="*60)
    print("\nYou will need:")
    print("  - Ice water bath (0°C)")
    print("  - Room temperature water (~20°C)")
    print("  - Hot water bath (60-80°C)")
    print("  - Boiling water (100°C)")
    print("  - Accurate thermometer")
    print("  - Multimeter connected to sensor output pin")
    print()
    
    calibration_points = []
    
    temps = [
        ("Ice water", 0.0),
        ("Room temperature", 20.0),
        ("Hot water", 60.0),
        ("Very hot water", 80.0),
        ("Boiling water", 100.0)
    ]
    
    print("For each temperature:")
    print("  1. Place sensor in bath")
    print("  2. Wait for stable reading")
    print("  3. Measure voltage with multimeter")
    print()
    
    for name, temp in temps:
        input(f"\nPress ENTER when sensor is in {name} ({temp}°C)...")
        
        try:
            voltage = float(input(f"Enter measured voltage (0-5V): "))
            
            if voltage < 0 or voltage > 5:
                print("⚠ Warning: Voltage out of range!")
            
            actual_temp = float(input(f"Enter actual temperature (°C) [{temp}]: ") or temp)
            
            calibration_points.append((voltage, actual_temp))
            print(f"✓ Recorded: {voltage:.3f}V = {actual_temp:.1f}°C")
            
        except ValueError:
            print("✗ Invalid input, skipping...")
    
    print("\n" + "="*60)
    print("CALIBRATION RESULTS - Add to calibration.h:")
    print("="*60)
    print("\nconst TempPoint COOLANT_TEMP_CURVE[] = {")
    for voltage, temp in calibration_points:
        print(f"    {{{voltage:.2f}, {temp:.1f}}},")
    print("};\n")
    
    return calibration_points

def calibrate_pressure():
    """Guide user through pressure sensor calibration"""
    print("\n" + "="*60)
    print("PRESSURE SENSOR CALIBRATION")
    print("="*60)
    print("\nYou will need:")
    print("  - Pressure gauge")
    print("  - Air compressor or pressure source")
    print("  - Multimeter connected to sensor output pin")
    print()
    
    calibration_points = []
    
    pressures = [0, 25, 50, 75, 100, 125, 150]
    
    print("For each pressure point:")
    print("  1. Set pressure source to target PSI")
    print("  2. Verify with pressure gauge")
    print("  3. Measure voltage with multimeter")
    print()
    
    for psi in pressures:
        input(f"\nPress ENTER when pressure is at {psi} PSI...")
        
        try:
            voltage = float(input(f"Enter measured voltage (0-5V): "))
            
            if voltage < 0 or voltage > 5:
                print("⚠ Warning: Voltage out of range!")
            
            actual_psi = float(input(f"Enter actual pressure (PSI) [{psi}]: ") or psi)
            
            calibration_points.append((voltage, actual_psi))
            print(f"✓ Recorded: {voltage:.3f}V = {actual_psi:.1f} PSI")
            
        except ValueError:
            print("✗ Invalid input, skipping...")
    
    print("\n" + "="*60)
    print("CALIBRATION RESULTS - Add to calibration.h:")
    print("="*60)
    print("\nconst PressurePoint OIL_PRESSURE_CURVE[] = {")
    for voltage, psi in calibration_points:
        print(f"    {{{voltage:.2f}, {psi:.1f}}},")
    print("};\n")
    
    return calibration_points

def calibrate_tps():
    """Guide user through TPS calibration"""
    print("\n" + "="*60)
    print("THROTTLE POSITION SENSOR CALIBRATION")
    print("="*60)
    print("\nYou will need:")
    print("  - Multimeter connected to TPS signal pin")
    print("  - Access to throttle body")
    print()
    
    input("\nPress ENTER when throttle is FULLY CLOSED...")
    min_voltage = float(input("Enter measured voltage (0-5V): "))
    print(f"✓ Min voltage: {min_voltage:.3f}V")
    
    input("\nPress ENTER when throttle is WIDE OPEN (WOT)...")
    max_voltage = float(input("Enter measured voltage (0-5V): "))
    print(f"✓ Max voltage: {max_voltage:.3f}V")
    
    print("\n" + "="*60)
    print("CALIBRATION RESULTS - Add to calibration.h:")
    print("="*60)
    print(f"\nconst float TPS_MIN_VOLTAGE = {min_voltage:.2f};  // Closed throttle")
    print(f"const float TPS_MAX_VOLTAGE = {max_voltage:.2f};  // Wide Open Throttle\n")

def main():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║      MX5 DAQ - Sensor Calibration Helper Tool         ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    print("Select calibration type:")
    print("  1. Temperature Sensor (Coolant/Oil)")
    print("  2. Pressure Sensor (Oil Pressure)")
    print("  3. Throttle Position Sensor (TPS)")
    print("  4. All of the above")
    print("  5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == '1':
        calibrate_temperature()
    elif choice == '2':
        calibrate_pressure()
    elif choice == '3':
        calibrate_tps()
    elif choice == '4':
        calibrate_temperature()
        calibrate_pressure()
        calibrate_tps()
    elif choice == '5':
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")
        return
    
    print("\n" + "="*60)
    print("Calibration complete!")
    print("Copy the code above into firmware/src/calibration.h")
    print("Then re-upload firmware to Arduino")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCalibration interrupted by user.")
        sys.exit(0)
