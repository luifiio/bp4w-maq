#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>

class TemperatureSensor {
public:
    TemperatureSensor(int pin);
    float readCelsius();
    float readRaw();
    
private:
    int _pin;
    float voltageToTemp(float voltage);
};

class PressureSensor {
public:
    PressureSensor(int pin);
    float readPSI();
    float readBar();
    
private:
    int _pin;
    float voltageToPressure(float voltage);
};

class ThrottlePositionSensor {
public:
    ThrottlePositionSensor(int pin);
    float readPercent();
    
private:
    int _pin;
};

// Utility functions
float readAnalogVoltage(int pin);

#endif