import argparse
import threading
from flask import Flask, Blueprint, jsonify, request
from queue import Queue

from serialhandler.serialhandler import serial_handler_instance
import background.background as background
import httpserver.httpserver as httpserver

argparser = argparse.ArgumentParser(description="Serial Server\n" \
                                    "  read and write data from serial port and provide HTTP API"
                                    , formatter_class=argparse.RawDescriptionHelpFormatter)
argparser.add_argument("-p", "--port", type=int, default=7878, help="Port number for the HTTP server (default: 7878)")
args = argparser.parse_args()

if __name__ == "__main__":
    port_number = args.port
    serial_handler = serial_handler_instance
    dataQueue, read_thread = serial_handler.get_serial_thread()
    background_thread = background.get_background_thread(dataQueue)
    read_thread.start()
    background_thread.start()
    app_main = Flask(__name__)
    app_main.register_blueprint(httpserver.app)

    app_main.run(host='127.0.0.1', port=port_number)

