from serial import Serial
import serial
import serial.tools.list_ports as list_ports
import lib.cobs as cobs
from lib.parsermanager import ParserManager
import threading
from queue import Queue


class serial_handler:
    def __init__(self):
        self.ser = None
        self.read_thread = None
        self.parser_manager = ParserManager()
        self.queue = Queue(10)

    def list_serial_ports(self):
        for port in list_ports.comports():
            print(f"Port: {port.device}, Description: {port.description}, HWID: {port.hwid}")

    def connect(self, portname: str, baudrate: int = 9600) -> bool:
        try:
            self.ser = Serial(portname, baudrate, timeout=1)
            print(f"Connected to {portname} at {baudrate} baud.")
            return True
        except serial.SerialException as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Disconnected.")
        else:
            print("Serial port is not open.")

    def read_data(self):
        if not self.ser or not self.ser.is_open:
            print("Serial port is not open. Cannot read data.")
            return
        while True:
            data_buf = bytes()
            try:
                data = self.ser.read_until(b'\x00')
                print(f"Raw data received: {data.hex()}")
                data_buf += data[:-1]
                if (data.endswith(b'\x00')):
                    decoded_data, _ = cobs.cobs_decode(data)
                    parsed_data, parser_name = self.parser_manager.parse_data(bytes(decoded_data))
                    if parser_name is None:
                        print("No parser found for the data.")
                    else:
                        self.queue.put((parsed_data, parser_name))
                        print(f"Received data: {parsed_data}")
                    data_buf = bytes()
            except serial.SerialTimeoutException as e:
                print(f"Error: {e}")


    def run_read_thread(self) -> Queue:
        if self.ser and self.ser.is_open:
            self.read_thread = threading.Thread(target=self.read_data, daemon=True)
            self.read_thread.start()
            return self.queue
        else:
            print("Serial port is not open. Cannot start read thread.")
            return None