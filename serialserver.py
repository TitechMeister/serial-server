import argparse
import threading
from flask import Flask, Blueprint, jsonify, request
from queue import Queue

import serialhandler.serialhandler as serial_handler
import background.background as background
import httpserver.httpserver as httpserver

argparser = argparse.ArgumentParser(description="Serial Server\n" \
                                    "  read and write data from serial port and provide HTTP API"
                                    , formatter_class=argparse.RawDescriptionHelpFormatter)
argparser.add_argument("-p", "--port", type=int, default=7878, help="Port number for the HTTP server (default: 7878)")
args = argparser.parse_args()

if __name__ == "__main__":
    port_number = args.port
    serial_handler_instance = serial_handler.serial_handler()
    dataQueue, read_thread = serial_handler_instance.get_serial_thread()
    background_instance = background.Background(dataQueue)
    background_thread = background_instance.get_background_thread(dataQueue)
    read_thread.start()
    background_thread.start()

    app_main = Flask(__name__)
    app_main.config["serial_handler_instance"] = serial_handler_instance
    app_main.config["background_instance"] = background_instance
    app_main.register_blueprint(httpserver.app)

    app_main.run(host='127.0.0.1', port=port_number)

