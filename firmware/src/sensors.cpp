#include "sensors.h"
#include "config.h"
#include "calibration.h"

// Temperature Sensor Implementation
TemperatureSensor::TemperatureSensor(int pin) : _pin(pin) {
    pinMode(_pin, INPUT);
}

float TemperatureSensor::readCelsius() {
    float voltage = readAnalogVoltage(_pin);
    return voltageToTemp(voltage);
}

float TemperatureSensor::readRaw() {
    return readAnalogVoltage(_pin);
}

float TemperatureSensor::voltageToTemp(float voltage) {
    // Validate voltage range
    if (voltage < 0.0 || voltage > VREF) {
        return NAN; // Invalid reading
    }
    
    // Use lookup table interpolation from calibration.h
    return Calibration::lookupTemperature(voltage, 
                                         Calibration::COOLANT_TEMP_CURVE, 
                                         Calibration::COOLANT_CURVE_SIZE);
}

// Pressure Sensor Implementation
PressureSensor::PressureSensor(int pin) : _pin(pin) {
    pinMode(_pin, INPUT);
}

float PressureSensor::readPSI() {
    float voltage = readAnalogVoltage(_pin);
    return voltageToPressure(voltage);
}

float PressureSensor::readBar() {
    return readPSI() * 0.0689476; // PSI to bar
}

float PressureSensor::voltageToPressure(float voltage) {
    // Validate voltage range
    if (voltage < 0.0 || voltage > VREF) {
        return NAN; // Invalid reading
    }
    
    // Use lookup table interpolation from calibration.h
    return Calibration::lookupPressure(voltage, 
                                      Calibration::OIL_PRESSURE_CURVE, 
                                      Calibration::PRESSURE_CURVE_SIZE);
}

// Throttle Position Sensor Implementation
ThrottlePositionSensor::ThrottlePositionSensor(int pin) : _pin(pin) {
    pinMode(_pin, INPUT);
}

float ThrottlePositionSensor::readPercent() {
    float voltage = readAnalogVoltage(_pin);
    
    // Validate voltage range
    if (voltage < 0.0 || voltage > VREF) {
        return NAN; // Invalid reading
    }
    
    // Use calibrated min/max from calibration.h
    float percent = ((voltage - Calibration::TPS_MIN_VOLTAGE) / 
                    (Calibration::TPS_MAX_VOLTAGE - Calibration::TPS_MIN_VOLTAGE)) * 100.0;
    
    // Clamp to 0-100%
    if (percent < 0.0) return 0.0;
    if (percent > 100.0) return 100.0;
    return percent;
}

// Utility Functions
float readAnalogVoltage(int pin) {
    // Multi-sample averaging for noise reduction
    const int NUM_SAMPLES = 10;
    unsigned long sum = 0;
    
    for (int i = 0; i < NUM_SAMPLES; i++) {
        sum += analogRead(pin);
        delayMicroseconds(100); // Small delay between samples
    }
    
    float avgValue = sum / (float)NUM_SAMPLES;
    return (avgValue / ADC_RESOLUTION) * VREF;
}