from flask import Flask, request, render_template_string, url_for
import serial
import time
import glob

app = Flask(__name__)

def find_arduino_port():
    ports = glob.glob('/dev/cu.usbmodem*')
    if ports:
        return ports[0]
    #else:
    #    raise serial.SerialException("No Arduino connected")

def open_serial_port(baudrate, retries=5):
    while retries > 0:
        try:
            port = find_arduino_port()
            ser = serial.Serial(port, baudrate)
            return ser
        except serial.SerialException as e:
            print(f"Error opening port: {e}")
            retries -= 1
            time.sleep(1)
    raise serial.SerialException("Could not open port after multiple attempts")

ser = open_serial_port(9600)

HTML_MAIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NANOBUBBLE GENERATOR</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f2eeff;
        }
        .button {
            padding: 15px 30px;
            font-size: 20px;
            margin: 10px;
            cursor: pointer;
        }
        .description {
            font-size: 14px;
            margin: 5px 0 20px 0;
        }
        .drifting {
            position: absolute;
        }
        #toggleButton {
            position: relative;
        }
        #footer {
            position: absolute;
            bottom: 10px;
            width: 100%;
            text-align: center;
        }
        #logo {
            position: absolute;
            bottom: 10px;
            left: 10px;
            width: 200px; /* Adjust size as needed */
        }
        #logo2 {
            position: absolute;
            bottom: -50px;
            right: 20px;
            width: 200px; /* Adjust size as needed */
        }
    </style>
    <script>
        let advancedMode = false;
        let intervalId;

        function toggleMode() {
            advancedMode = !advancedMode;
            const buttons = document.querySelectorAll('.button:not(#toggleButton)');
            const toggleButton = document.getElementById('toggleButton');

            if (advancedMode) {
                toggleButton.innerText = 'Simple Mode';
                buttons.forEach(button => button.classList.add('drifting'));
                intervalId = setInterval(moveButtons, 100);
            } else {
                toggleButton.innerText = 'Advanced Mode';
                buttons.forEach(button => {
                    button.classList.remove('drifting');
                    button.style.top = '';
                    button.style.left = '';
                });
                clearInterval(intervalId);
            }
        }

        function moveButtons() {
            const buttons = document.querySelectorAll('.drifting');
            buttons.forEach(button => {
                const x = Math.random() * (window.innerWidth - button.clientWidth);
                const y = Math.random() * (window.innerHeight - button.clientHeight);
                button.style.top = y + 'px';
                button.style.left = x + 'px';
            });
        }
    </script>
</head>
<body>
    <img src="{{ url_for('static', filename='logo.png') }}" id="logo" alt="Logo">
    <img src="{{ url_for('static', filename='logo2.png') }}" id="logo2" alt="Logo2">
    <h1>NANOBUBBLE GENERATOR</h1>
    <p><b>SET-UP Instructions</b><br>1. Add distilled water in the source container<br>2. Remove contents from the waste container<br>3. Set the hotplate at the required temperature</p>
    <form action="/load" method="get">
        <button type="submit" class="button">LOAD</button>
        <p class="description">This function loads the syringe with the required volume of water, ensuring thermal equilibrium.</p>
    </form>
    <form action="/generate" method="get">
        <button type="submit" class="button">GENERATE</button>
        <p class="description">This function generates the nanobubbles, by controlling the speed and number of pulling cycles.</p>
    </form>
    <form action="/flush" method="get">
        <button type="submit" class="button">FLUSH</button>
        <p class="description">This function flushes the nanobubbles through the DLS, and then cleans the system for next use.</p>
    </form>
    <div id="footer">
        <button id="toggleButton" class="button" onclick="toggleMode()">Advanced Mode</button>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f2eeff;
        }
        input, button {
            padding: 10px;
            font-size: 16px;
            margin: 10px;
        }
        .top-left, .top-right, .bottom-right {
            position: absolute;
            padding: 10px 20px;
            font-size: 16px;
        }
        .top-left {
            top: 10px;
            left: 10px;
        }
        .top-right {
            top: 10px;
            right: 10px;
        }
        .bottom-right {
            bottom: 10px;
            right: 10px;
        }
        .box {
            border: 1px solid #000;
            padding: 15px;
            margin: 15px 0;
            text-align: left;
        }
    </style>
    <script>
    function sendCommand() {
        const title = document.querySelector('h1').innerText;
        let url = `/control?command=`;

        if (title === 'LOAD') {
            const volume = document.getElementById('volume').value;
            if (volume === '') {
                alert("Please enter the volume before starting.");
                return;
            }
            url += `load&volume=${volume}`;
        } else if (title === 'GENERATE') {
            const pullingSpeed = document.getElementById('pullingSpeed').value;
            const pushingSpeed = document.getElementById('pushingSpeed').value;
            const cycles = document.getElementById('cycles').value;

            if (pullingSpeed === '' || pushingSpeed === '' || cycles === '') {
                alert("Please enter all values before starting.");
                return;
            }
            url += `generate&pullingSpeed=${pullingSpeed}&pushingSpeed=${pushingSpeed}&cycles=${cycles}`;
        }

        console.log('Sending request to:', url);  // Log the URL to verify

        fetch(url)
            .then(response => response.text())
            .then(data => {
                alert(data);
                document.getElementById('nextButton').disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while sending the command.');
            });
    }

    function sendAnalysisCommand() {
        fetch(`/control?command=analysis`)
            .then(response => response.text())
            .then(data => {
                alert(data);
                document.getElementById('nextButton').disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while sending the command.');
            });
    }

    function sendCleanUpCommand() {
        fetch(`/control?command=cleanup`)
            .then(response => response.text())
            .then(data => {
                alert(data);
                document.getElementById('nextButton').disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while sending the command.');
            });
    }
    </script>
</head>
<body>
    <button class="top-left" onclick="location.href='/'">BACK TO MENU</button>
    <button class="top-right" onclick="sendCommand()">START</button>
    <button id="nextButton" class="bottom-right" onclick="location.href='{{ next_url }}'" disabled>NEXT</button>
    <h1>{{ title }}</h1>
    {% if title == 'LOAD' %}
        <div class="box">
            This function loads the syringe with the required volume of water, ensuring thermal equilibrium.
        </div>
        <div class="box">
            <h3>ANALYTE SOLUTION VOLUME</h3>
            Volumes need to be larger than 10mL to ensure they reach the DLS, but smaller than 20mL to ensure there is enough space for the pulling motion on the syringe.
            <input type="number" id="volume" name="volume" placeholder="mL"><br>
        </div>
    {% elif title == 'GENERATE' %}
        <div class="box">
            Controlling the speed and number of pulling cycles.
        </div>
        <div class="box">
            <h3>Pulling Speed</h3>
            This is the speed at which liquid is pulled under vacuum in the syringe.
            <input type="number" id="pullingSpeed" name="pullingSpeed" placeholder="cm/s"><br>
        </div>
        <div class="box">
            <h3>Pushing Speed</h3>
            This is the speed at which the liquid returns to its initial volume in the syringe.
            <input type="number" id="pushingSpeed" name="pushingSpeed" placeholder="cm/s"><br>
        </div>
        <div class="box">
            <h3>Number of Cycles</h3>
            This is the number of pulling-pushing repetitions.
            <input type="number" id="cycles" name="cycles"><br>
        </div>
    {% elif title == 'FLUSH' %}
        <div class="box">
            Through the DLS, and then cleans the system for the next use.
        </div>
        <div class="box">
            <h3>Analysis</h3>
            Make sure the DLS is ready, and then press start analysis to push the nanobubbles through it. The progress bar shows how much of the liquid has been pushed by the syringe.
            <button type="button" onclick="sendAnalysisCommand()">Start Analysis</button><br>
        </div>
        <div class="box">
            <h3>Clean-Up</h3>
            When the experiment is done, press start to clean-up the tubing with uncontaminated distilled water from the source. Make sure there is still plenty left.
            <button type="button" onclick="sendCleanUpCommand()">Start Clean-Up</button><br>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_MAIN)

@app.route('/load')
def load():
    return render_template_string(HTML_TEMPLATE, title="LOAD", next_url=url_for('generate'))

@app.route('/generate')
def generate():
    return render_template_string(HTML_TEMPLATE, title="GENERATE", next_url=url_for('flush'))

@app.route('/flush')
def flush():
    return render_template_string(HTML_TEMPLATE, title="FLUSH", next_url=url_for('index'))

@app.route('/control', methods=['GET'])
def control():
    volume = request.args.get('volume')
    pulling_speed = request.args.get('pullingSpeed')
    pushing_speed = request.args.get('pushingSpeed')
    cycles = request.args.get('cycles')
    command = request.args.get('command')

    if command == 'load' and volume:
        ser.write(f'L{volume}\n'.encode())
        return f"Load command sent with volume {volume} mL"
    elif command == 'generate' and pulling_speed and pushing_speed and cycles:
        ser.write(f'G{pulling_speed},{pushing_speed},{cycles}\n'.encode())
        return f"Pulling speed: {pulling_speed}, Pushing speed: {pushing_speed}, Number of cycles: {cycles}"
    elif command == 'analysis':
        ser.write('A\n'.encode())
        return "Analysis started"
    elif command == 'cleanup':
        ser.write('C\n'.encode())
        return "Clean-up started"
    else:
        return "Invalid command"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

