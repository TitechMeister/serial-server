from lib.abstractparser import AbstractParser
import struct

class UltrasonicParser(AbstractParser):
    """
    Parser for ultrasonic sensor data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BxxxIff")

    @staticmethod
    def get_name() -> str:
        return "Ultrasonic"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "altitude", "temperature"]

    @staticmethod
    def get_data_length() -> int:
        return 16

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\x50')]  # Assuming the first byte is the ID for ultrasonic sensor

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, timestamp, altitude, temperature = self.parser.unpack(data)
        return {
            "timestamp": timestamp,
            "altitude": altitude,
            "temperature": temperature
        }

parser = UltrasonicParser()