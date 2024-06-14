#include <AccelStepper.h>

// Define pin connections
#define CW_PIN 9 // Clockwise rotation
#define CCW_PIN 8 // Counter-clockwise rotation
#define ENABLE_PIN 7
#define VALVE1_PIN 4
#define VALVE2_PIN 5

// Steps per mL
const int stepsPerML = 5000 * 14 / 20; // Calculate steps per mL
long loadingSpeed = 20000;
long loadingVolume;
long loadingAccel = 20000;
long maxAccel = 100000;

// Create an instance of AccelStepper
AccelStepper stepperCW(AccelStepper::DRIVER, CW_PIN, -1); // Clockwise only
AccelStepper stepperCCW(AccelStepper::DRIVER, CCW_PIN, -1); // Counter-clockwise only

void setup() {
  Serial.begin(9600);
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(VALVE1_PIN, OUTPUT);
  pinMode(VALVE2_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, HIGH); // Enable the motor initially
  digitalWrite(VALVE1_PIN, LOW); // Valves start closed
  digitalWrite(VALVE2_PIN, LOW); // Valves start closed

  // Set the maximum speed and acceleration for both directions
  stepperCW.setMaxSpeed(loadingSpeed); // Set your desired max speed
  stepperCW.setAcceleration(loadingAccel); // Set your desired acceleration

  stepperCCW.setMaxSpeed(loadingSpeed); // Set your desired max speed
  stepperCCW.setAcceleration(loadingAccel); // Set your desired acceleration

  Serial.println("Setup completed");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    char command = input.charAt(0);
    long value1 = input.substring(1, input.indexOf(',')).toInt();
    long value2 = input.substring(input.indexOf(',') + 1, input.lastIndexOf(',')).toInt();
    long value3 = input.substring(input.lastIndexOf(',') + 1).toInt();

    // FIRST FUNCTION = LOADING FUNCTION -----------------------------------------------------

    if (command == 'L') {
      long steps = value1 * 333.3 * 10;
      long calib_steps = 66666;
      loadingVolume = value1;

      Serial.println("Load command received with steps: " + String(steps));

      for (int i = 0; i < 2; i++) {
        Serial.println("Cycle " + String(i + 1) + " started");

        // Open Valve 1
        digitalWrite(VALVE1_PIN, HIGH);
        delay(1000); // Allow time for the valve to open

        // Pulling motion (Counter-Clockwise)
        stepperCCW.setCurrentPosition(0); // Reset position
        stepperCCW.setSpeed(loadingSpeed);
        stepperCCW.moveTo(calib_steps); // Move steps
        while (stepperCCW.distanceToGo() != 0) {
          stepperCCW.run();
        }

        // Close Valve 1
        digitalWrite(VALVE1_PIN, LOW);
        delay(1000); // Allow time for the valve to close

        // Open Valve 2
        digitalWrite(VALVE2_PIN, HIGH);
        delay(1000); // Allow time for the valve to open

        // Pushing motion (Clockwise)
        stepperCW.setCurrentPosition(0); // Reset position
        stepperCW.setSpeed(loadingSpeed);
        stepperCW.moveTo(calib_steps); // Move steps
        while (stepperCW.distanceToGo() != 0) {
          stepperCW.run();
        }

        // Close Valve 2
        digitalWrite(VALVE2_PIN, LOW);
        delay(1000); // Allow time for the valve to close

        Serial.println("Cycle " + String(i + 1) + " completed");
      }

      // Final operation
      digitalWrite(VALVE1_PIN, HIGH);
      delay(1000); // Allow time for the valve to open

      // Pulling motion (Counter-Clockwise)
      stepperCCW.setCurrentPosition(0); // Reset position
      stepperCCW.setSpeed(loadingSpeed);
      stepperCCW.moveTo(steps); // Move steps
      while (stepperCCW.distanceToGo() != 0) {
        stepperCCW.run();
      }

      // Close Valve 1
      digitalWrite(VALVE1_PIN, LOW);
      delay(1000); // Allow time for the valve to close

      Serial.println("Loading completed with final pulling motion");

    // FUNCTION 2: GENERATING -----------------------------------------------------------------------------------  
    } else if (command == 'G') {
      int pullingSpeed = value1;
      int pushingSpeed = value2;
      int cycles = value3;
      long pullingStep = (long)(((18.0 - loadingVolume) / (20.0 * pullingSpeed)) * (66666.0 * loadingSpeed));
      long pushingStep = (long)(((18.0 - loadingVolume) / (20.0 * pushingSpeed)) * (66666.0 * loadingSpeed));
      stepperCW.setAcceleration(maxAccel);
      stepperCCW.setAcceleration(maxAccel);

      Serial.println("Received command:");
      Serial.println("Pulling Speed: " + String(pullingSpeed));
      Serial.println("Pushing Speed: " + String(pushingSpeed));
      Serial.println("Cycles: " + String(cycles));

      digitalWrite(ENABLE_PIN, HIGH); // Enable the motor

      for (int i = 0; i < cycles; i++) {
        Serial.println("Cycle " + String(i + 1) + " started");

        // Pulling motion (Counter-Clockwise)
        //stepperCCW.setCurrentPosition(0); // Reset position
        stepperCCW.setSpeed(pullingSpeed);
        Serial.println("Pulling speed = " + String(pullingSpeed));
        Serial.println("Pulling step = " + String(pullingStep));
        stepperCCW.moveTo(pullingStep); // Move steps
        int step = 0;
        while (stepperCCW.distanceToGo() != 0) {
          stepperCCW.run();
          step += 1;
          Serial.println("Step number:" + String(step));
        }
        step = 0;
        // Pushing motion (Clockwise)
        //stepperCW.setCurrentPosition(0); // Reset position
        stepperCW.setSpeed(pushingSpeed);
        stepperCW.moveTo(pushingStep); // Move steps
        Serial.println("Pushing speed = " + String(pushingSpeed));
        Serial.println("Pushing step = " + String(pushingStep));
        while (stepperCW.distanceToGo() != 0) {
          stepperCCW.run();
          step += 1;
          Serial.println("Step number:" + String(step));
        }

        Serial.println("Cycle " + String(i + 1) + " completed");
      }

      digitalWrite(ENABLE_PIN, LOW); // Disable the motor after running
      Serial.println("Pulling and pushing completed for " + String(cycles) + " cycles");
    } else if (command == 'A') {
      Serial.println("Analysis started");

      int steps = value1 * stepsPerML;

      // Open Valve 2
      digitalWrite(VALVE2_PIN, HIGH);
      delay(1000); // Allow time for the valve to open

      // Turn motor CCW at set speed
      stepperCCW.setCurrentPosition(0); // Reset position
      stepperCCW.setSpeed(5000);
      stepperCCW.moveTo(steps); // Use the volume from load stage
      while (stepperCCW.distanceToGo() != 0) {
        stepperCCW.run();
      }

      // Close Valve 2
      digitalWrite(VALVE2_PIN, LOW);
      delay(1000); // Allow time for the valve to close
    } else if (command == 'C') {
      Serial.println("Clean-up started");

      for (int i = 0; i < 5; i++) {
        int steps = value1 * stepsPerML;

        // Open Valve 1
        digitalWrite(VALVE1_PIN, HIGH);
        delay(1000);

        // Pulling motion (Counter-Clockwise)
        stepperCCW.setCurrentPosition(0); // Reset position
        stepperCCW.setSpeed(loadingSpeed);
        stepperCCW.moveTo(steps); // Move steps
        while (stepperCCW.distanceToGo() != 0) {
          stepperCCW.run();
        }

        // Close Valve 1
        digitalWrite(VALVE1_PIN, LOW);
        delay(1000); // Allow time for the valve to close

        // Open Valve 2
        digitalWrite(VALVE2_PIN, HIGH);
        delay(1000); // Allow time for the valve to open

        // Pushing motion (Clockwise)
        stepperCW.setCurrentPosition(0); // Reset position
        stepperCW.setSpeed(loadingSpeed);
        stepperCW.moveTo(steps); // Move steps
        while (stepperCW.distanceToGo() != 0) {
          stepperCW.run();
        }

        // Close Valve 2
        digitalWrite(VALVE2_PIN, LOW);
        delay(1000); // Allow time for the valve to close
      }

      // Final operation
      int steps = value1 * stepsPerML;

      digitalWrite(VALVE1_PIN, HIGH);
      delay(1000); // Allow time for the valve to open

      // Pulling motion (Counter-Clockwise)
      stepperCCW.setCurrentPosition(0); // Reset position
      stepperCCW.setSpeed(loadingSpeed);
      stepperCCW.moveTo(steps); // Move steps
      while (stepperCCW.distanceToGo() != 0) {
        stepperCCW.run();
      }

      // Close Valve 1
      digitalWrite(VALVE1_PIN, LOW);
      delay(1000); // Allow time for the valve to close

      Serial.println("Clean-up completed");
    }
  }
}
