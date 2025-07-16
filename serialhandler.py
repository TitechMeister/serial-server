import time
from serial import Serial
import serial
import serial.tools.list_ports as list_ports
import threading
from queue import Queue

import lib.cobs as cobs
from lib.parsermanager import ParserManager
import shared_data

class serial_handler:
    def __init__(self):
        self.ser = None
        self.read_thread = None
        self.parser_manager = ParserManager()
        self.queue = Queue(10)

    def list_serial_ports(self) -> list[dict[str, str, str]]:
        available_ports = []
        for port in list_ports.comports():
            print(f"Port: {port.device}, Description: {port.description}, HWID: {port.hwid}")
            available_ports.append({"device": port.device, "description": port.description, "hwid": port.hwid})
        return available_ports

    def connect(self, portname: str, baudrate: int = 9600, timeout=1) -> bool:
        if self.ser and self.ser.is_open:
            print("Already connected to a serial port. Disconnect it.")
            self.disconnect()
        try:
            self.ser = Serial(portname, baudrate, timeout=timeout)
            with shared_data.state_lock:
                shared_data.serial_state = shared_data.SerialState.CONNECTED
            print(f"Connected to {portname} at {baudrate} baud.")
            return True
        except serial.SerialException as e:
            print(f"Connection error: {e}")
            with shared_data.state_lock:
                shared_data.serial_state = shared_data.SerialState.ERROR
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            with shared_data.state_lock:
                shared_data.serial_state = shared_data.SerialState.DISCONNECTED
            print("Disconnected.")
            return True
        else:
            print("Serial port is not open.")
            return False

    def get_parser_names(self) -> list[str]:
        """
        Returns a list of available parser names.
        """
        return self.parser_manager.get_parser_names()


    def read_data(self):
        """
        Continuously reads data from the serial port and processes it.
        If the state changes to something other than READING, it stops reading.
        """
        if not self.ser or not self.ser.is_open:
            print("Serial port is not open. Cannot start reading.")
            return
        with shared_data.state_lock:
            shared_data.serial_state = shared_data.SerialState.READING
        current_state = shared_data.SerialState.READING
        while True:
            # Check if the state has changed by other threads
            if shared_data.state_lock.acquire(timeout=0.1):
                try:
                    current_state = shared_data.serial_state
                finally:
                    shared_data.state_lock.release()
            if current_state != shared_data.SerialState.READING:
                print("Reading stopped due to state change.")
                return

            data_buf = bytes()
            try:
                data = self.ser.read_until(b'\x00')
                if not data:
                    threading.Event().wait(0.05)  # Wait a bit before trying to read again
                    continue
                print(f"Raw data received: {data.hex()}")
                data_buf += data[:-1]
                if (data.endswith(b'\x00')):
                    decoded_data, _ = cobs.cobs_decode(data)
                    parsed_data, parser_name = self.parser_manager.parse_data(bytes(decoded_data))
                    if parser_name is None:
                        print("No parser found for the data.")
                    else:
                        parsed_data["received_time"] = int(time.time() * 1000)  # Add received time in milliseconds
                        self.queue.put((parsed_data, parser_name))
                        print(f"Received data: {parsed_data}")
                    data_buf = bytes()
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                self.queue.put((None, None))
                with shared_data.state_lock:
                    shared_data.serial_state = shared_data.SerialState.ERROR
                return 

    def serial_handle(self):
        """
        Starts the serial handler, which includes reading data from the serial port.
        If the read fails, it will attempt to reconnect.

        If you want to open, close or change serial port,
        you should call the connect or disconnect methods from outside this thread.
        It will stop reading and wait for the next connection attempt.
        """
        while True:
            self.read_data()  # returns when the state changes
            threading.Event().wait(1)  # Wait before trying to reconnect

    def get_serial_thread(self) -> tuple[Queue, threading.Thread]:
        self.serial_thread = threading.Thread(target=self.serial_handle, daemon=True)
        return self.queue, self.serial_thread


serial_handler_instance = serial_handler()