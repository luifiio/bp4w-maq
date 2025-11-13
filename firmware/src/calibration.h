#ifndef CALIBRATION_H
#define CALIBRATION_H

#include <Arduino.h>

// Coolant Temperature Sensor Calibration
// Mazda MX5 typically uses NTC thermistor (negative temperature coefficient)
// These are example values - calibrate with your actual sensor!
namespace Calibration {
    struct TempPoint {
        float voltage;
        float celsius;
    };
    
    // Coolant temperature calibration curve
    // TODO: Replace with actual measurements from your sensor
    // Method: Use boiling water (100°C), ice water (0°C), and room temp to calibrate
    const TempPoint COOLANT_TEMP_CURVE[] = {
        {0.5, -10.0},   // Cold
        {1.0, 10.0},
        {1.5, 30.0},
        {2.0, 50.0},
        {2.5, 70.0},
        {3.0, 85.0},    // Normal operating
        {3.5, 100.0},
        {4.0, 115.0},   // Hot
        {4.5, 130.0}
    };
    
    const int COOLANT_CURVE_SIZE = sizeof(COOLANT_TEMP_CURVE) / sizeof(TempPoint);
    
    // Oil pressure sensor calibration
    // Common automotive pressure senders: 0.5V = 0 PSI, 4.5V = 150 PSI
    struct PressurePoint {
        float voltage;
        float psi;
    };
    
    const PressurePoint OIL_PRESSURE_CURVE[] = {
        {0.5, 0.0},
        {1.5, 37.5},
        {2.5, 75.0},
        {3.5, 112.5},
        {4.5, 150.0}
    };
    
    const int PRESSURE_CURVE_SIZE = sizeof(OIL_PRESSURE_CURVE) / sizeof(PressurePoint);
    
    // Throttle Position Sensor calibration
    // Calibrate these by measuring voltage at closed throttle and WOT
    const float TPS_MIN_VOLTAGE = 0.5;  // Closed throttle
    const float TPS_MAX_VOLTAGE = 4.5;  // Wide Open Throttle
    
    // Linear interpolation helper function
    inline float interpolate(float x, float x0, float y0, float x1, float y1) {
        if (x1 == x0) return y0;
        return y0 + (x - x0) * (y1 - y0) / (x1 - x0);
    }
    
    // Lookup table interpolation for temperature
    inline float lookupTemperature(float voltage, const TempPoint* curve, int size) {
        // Out of range checks
        if (voltage <= curve[0].voltage) return curve[0].celsius;
        if (voltage >= curve[size-1].voltage) return curve[size-1].celsius;
        
        // Find the right segment and interpolate
        for (int i = 0; i < size - 1; i++) {
            if (voltage >= curve[i].voltage && voltage <= curve[i+1].voltage) {
                return interpolate(voltage, 
                                 curve[i].voltage, curve[i].celsius,
                                 curve[i+1].voltage, curve[i+1].celsius);
            }
        }
        return NAN; // Should never reach here
    }
    
    // Lookup table interpolation for pressure
    inline float lookupPressure(float voltage, const PressurePoint* curve, int size) {
        // Out of range checks
        if (voltage <= curve[0].voltage) return curve[0].psi;
        if (voltage >= curve[size-1].voltage) return curve[size-1].psi;
        
        // Find the right segment and interpolate
        for (int i = 0; i < size - 1; i++) {
            if (voltage >= curve[i].voltage && voltage <= curve[i+1].voltage) {
                return interpolate(voltage, 
                                 curve[i].voltage, curve[i].psi,
                                 curve[i+1].voltage, curve[i+1].psi);
            }
        }
        return NAN; // Should never reach here
    }
}

#endif