#include <Arduino.h>

// Define the motor driver pins
const int enablePin = 9;  // Enable pin for motor speed control (PWM capable pin)
const int input1Pin = 2;  // Input pin 1 for motor direction
const int input2Pin = 3;  // Input pin 2 for motor direction

void setup() {
  // Initialize Serial communication
  Serial.begin(9600);

  // Set the motor driver pins as outputs
  pinMode(enablePin, OUTPUT);
  pinMode(input1Pin, OUTPUT);
  pinMode(input2Pin, OUTPUT);

  // Set an initial direction
  digitalWrite(input1Pin, HIGH);
  digitalWrite(input2Pin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming byte (0 - 255)
    int speedValue = Serial.parseInt();

    // Map the input speed value (assumed to be 0 - 100 for percentage) to 0 - 255 for PWM
    int pwmValue = map(speedValue, 0, 100, 0, 255);

    // Safety check to ensure PWM values are within bounds
    pwmValue = constrain(pwmValue, 0, 255);

    // Set the motor speed
    analogWrite(enablePin, pwmValue);

    // Print the set speed to the Serial Monitor
    Serial.print("Motor speed set to: ");
    Serial.println(speedValue);
  }
}
