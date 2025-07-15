import serialhandler
# import background
import threading
from flask import Flask, Blueprint, jsonify, request
from queue import Queue


app = Blueprint("api", __name__)
data_lock = threading.Lock()
data_dict = {}


def latest_data_dict(queue: Queue):
    """
    Continuously fetches the latest data from the queue.
    This function runs in a separate thread.
    """
    while True:
        if not queue.empty():
            data = queue.get()
            print(f"Latest data: {data}")
            with data_lock:
                data_dict[data[1]] = data[0]  # Assuming data is a tuple (parsed_data, parser_name)
                print(f"Data stored for parser: {data[1]}, available parsers: {list(data_dict.keys())}")
        else:
            threading.Event().wait(0.05)  # Wait for 0.05 seconds before checking again

@app.route('/api/data', methods=['POST'])
def process_data():
    data = request.json
    # Process the data as needed
    return jsonify({"status": "success", "data": data})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "This is a test endpoint"})

@app.route('/data/<string:parsername>', methods=['GET'])
def parsed_data(parsername):
    with data_lock:
        data = data_dict.get(parsername)
        if data is None:
            return jsonify({"error": "No data found for this parser", "available": list(data_dict.keys())}), 404
        return jsonify(data)



if __name__ == "__main__":
    serial_handler = serialhandler.serial_handler()
    serial_handler.list_serial_ports()
    input_port = input("Enter port name to connect: ")
    if serial_handler.connect(input_port, 115200):
        dataQueue: Queue = serial_handler.run_read_thread()
        print("Serial handler is running.")
        threading.Thread(
            target=latest_data_dict,
            args=(dataQueue,),
            daemon=True
        ).start()
    app_main = Flask(__name__)
    app_main.register_blueprint(app)

    app_main.run(host='127.0.0.1', port=7878)

