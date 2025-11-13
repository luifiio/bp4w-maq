#include <Arduino.h>
#include "config.h"
#include "sensors.h"

// Sensor instances
TemperatureSensor coolantTemp(COOLANT_TEMP_PIN);
// Add other sensors as needed

unsigned long lastSampleTime = 0;

void setup() {
    Serial.begin(SERIAL_BAUD);
    
    // Wait for serial connection (useful for debugging)
    while (!Serial && millis() < 3000) {
        ; // Wait up to 3 seconds
    }
    
    Serial.println("MX5 DAQ System Starting...");
    Serial.println("timestamp_ms,coolant_temp_c");
}

void loop() {
    unsigned long currentTime = millis();
    
    // Sample at configured rate
    if (currentTime - lastSampleTime >= SAMPLE_PERIOD_MS) {
        lastSampleTime = currentTime;
        
        // Read sensors
        float coolantTempC = coolantTemp.readCelsius();
        
        // Output CSV format
        Serial.print(currentTime);
        Serial.print(",");
        Serial.println(coolantTempC, 2); // 2 decimal places
    }
}