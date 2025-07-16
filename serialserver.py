import threading
from flask import Flask, Blueprint, jsonify, request
from queue import Queue

import serialhandler
import background
import httpserver

if __name__ == "__main__":
    serial_handler = serialhandler.serial_handler()
    serial_handler.list_serial_ports()
    input_port = input("Enter port name to connect: ")
    if serial_handler.connect(input_port, 115200):
        dataQueue: Queue = serial_handler.run_read_thread()
        print("Serial handler is running.")
        threading.Thread(
            target=background.latest_data_dict,
            args=(dataQueue,),
            daemon=True
        ).start()
    app_main = Flask(__name__)
    app_main.register_blueprint(httpserver.app)

    app_main.run(host='127.0.0.1', port=7878)

