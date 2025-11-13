#ifndef CONFIG_H
#define CONFIG_H

// Pin Definitions
#define COOLANT_TEMP_PIN A0
#define OIL_TEMP_PIN A1
#define OIL_PRESSURE_PIN A2
#define THROTTLE_POS_PIN A3

// Sampling Configuration
#define SAMPLE_RATE_HZ 10
#define SAMPLE_PERIOD_MS (1000 / SAMPLE_RATE_HZ)

// Serial Configuration
#define SERIAL_BAUD 115200

// Voltage Reference
#define VREF 5.0
#define ADC_RESOLUTION 1023.0

// Enable/Disable Sensors
#define ENABLE_COOLANT_TEMP true
#define ENABLE_OIL_TEMP false
#define ENABLE_OIL_PRESSURE false
#define ENABLE_THROTTLE_POS false

#endif