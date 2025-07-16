import threading
from flask import Flask, Blueprint, jsonify, request
from queue import Queue

from serialhandler import serial_handler_instance
import background
import httpserver

if __name__ == "__main__":
    serial_handler = serial_handler_instance
    dataQueue, read_thread = serial_handler.get_serial_thread()
    background_thread = background.get_background_thread(dataQueue)
    read_thread.start()
    background_thread.start()
    app_main = Flask(__name__)
    app_main.register_blueprint(httpserver.app)

    app_main.run(host='127.0.0.1', port=7878)

