from flask import Blueprint, request, jsonify

import shared_data
from serialhandler import serial_handler_instance


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


