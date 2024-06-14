# Nanobubble Generator

This project includes a Python script for controlling an Arduino setup designed to load, generate, and flush nanobubbles. The Arduino code interfaces with various hardware components such as stepper motors and valves to perform the required operations. Below are the details and usage instructions for both the Python and Arduino scripts.

## Python Script

The Python script uses Flask to create a web interface for controlling the nanobubble generator. The web interface has three main functions: Load, Generate, and Flush, which correspond to different stages of the nanobubble generation process.

### Requirements

- Python 3.x
- Flask
- PySerial

### Installation

1. Install Flask and PySerial:
   ```bash
   pip install flask pyserial
   ```

2. Save the Python script as `app.py` and run it:
   ```bash
   python app.py
   ```

### Web Interface

- **Load**: This function loads the syringe with the required volume of water.
- **Generate**: This function controls the speed and number of pulling cycles to generate nanobubbles.
- **Flush**: This function flushes the nanobubbles through the DLS and cleans the system for the next use.

## Arduino Script

The Arduino script controls a stepper motor and valves to perform the operations required for loading, generating, and flushing nanobubbles.

### Hardware Requirements

- Arduino board
- Stepper motor
- Motor driver
- Valves
- Relay components
- 12V and 24V power supply
- Diodes (for back EMF)

### Usage

1. Upload the provided Arduino script to your Arduino board.
2. Ensure the hardware connections are made as per the pin definitions in the script.
3. Use the web interface to control the operations by clicking on the respective buttons for Load, Generate, and Flush.
