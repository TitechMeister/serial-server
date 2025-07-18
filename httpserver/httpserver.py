from flask import Blueprint, request, jsonify

import shared_data
from serialhandler.serialhandler import serial_handler_instance
import lib.cobs


app = Blueprint("api", __name__)

@app.route('/serial/state', methods=['GET'])
def get_serial_state():
    with shared_data.state_lock:
        state = shared_data.serial_state.name
    return jsonify({"state": state})

@app.route('/serial/available_ports', methods=['GET'])
def get_available_ports():
    ports = serial_handler_instance.list_serial_ports()
    return jsonify({"available_ports": ports})

@app.route('/serial/connect', methods=['POST'])
def connect_serial():
    data = request.json
    portname = data.get("portname")
    baudrate = data.get("baudrate", 115200)
    if not portname:
        return jsonify({"error": "Port name is required"}), 400
    success = serial_handler_instance.connect(portname, baudrate)
    if success:
        return jsonify({"status": "connected"})
    else:
        return jsonify({"error": "Failed to connect"}), 500
    
@app.route('/serial/disconnect', methods=['POST'])
def disconnect_serial():
    if serial_handler_instance.disconnect():
        return jsonify({"status": "disconnected"})
    else:
        return jsonify({"status": "port is not open"}), 204

@app.route('/serial/write', methods=['POST'])
def write_serial():
    data = request.json
    payload = data.get("payload")
    if not payload:
        return jsonify({"error": "Payload is required"}), 400
    try:
        encoded_payload = bytes(lib.cobs.cobs_encode(payload))
    except Exception as e:
        return jsonify({"error": f"Encoding error: {str(e)}"}), 500
    success = serial_handler_instance.write_data(encoded_payload)
    if success:
        return jsonify({"status": "data sent"})
    else:
        return jsonify({"error": "port is not open or failed to write"}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "This is a test endpoint"})

@app.route('/data/<string:parsername>', methods=['GET'])
def parsed_data(parsername):
    data = None
    with shared_data.data_lock:
        data = shared_data.data_dict.get(parsername)
    if data is None:
        return jsonify({"error": "No data found for this parser", "available": list(shared_data.data_dict.keys())}), 404
    return jsonify(data)

@app.route('/data', methods=['GET'])
def all_parsed_data():
    with shared_data.data_lock:
        data = shared_data.data_dict
    return jsonify(data)

@app.route('/parsers', methods=['GET'])
def get_parsers():
    parser_names = serial_handler_instance.get_parser_names()
    return jsonify({"parsers": parser_names})

@app.route('/parser/<parsername>', methods=['GET'])
def get_parser_information(parsername):
    info = serial_handler_instance.get_parser_information(parsername)
    if "error" in info:
        return jsonify(info), 404
    return jsonify(info)

@app.route('/help', methods=['GET'])
def help_page():
    help_content = """
    <html>
    <head>
        <title>Serial Server API Help</title>
    </head>
    <body>
        <h1>Serial Server API</h1>
        <p>This API allows you to interact with the serial server to manage serial connections and retrieve parsed data.</p>
        <p>Use the following endpoints to interact with the server:</p>
        <h2>API Endpoints</h2>
        <ul>
            <li><strong>/test</strong>: A test endpoint to check server functionality.</li>
            <li><strong>/serial/state</strong>: Get the current state of the serial connection.</li>
            <li><strong>/serial/available_ports</strong>: List all available serial ports.</li>
            <li><strong>/serial/connect</strong>: Connect to a specified serial port.</li>
            <li><strong>/serial/disconnect</strong>: Disconnect from the current serial port.</li>
            <li><strong>/data/&lt;parsername&gt;</strong>: Get parsed data for a specific parser.</li>
            <li><strong>/data</strong>: Get all parsed data from all parsers.</li>
            <li><strong>/parsers</strong>: List all available parsers.</li>
            <li><strong>/parser/&lt;parsername&gt;</strong>: Get information about a specific parser.</li>
        </ul>
        <h2>HELP</h2>
        <p>For more information on how to use the API, please refer to the
        <a href="https://github.com/TitechMeister/serial-server">documentation</a>.
    </body>
    </html>
    """
    return help_content, 200, {'Content-Type': 'text/html'}

@app.route('/', methods=['GET'])
def root():
    return help_page()