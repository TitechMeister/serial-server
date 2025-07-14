from lib.abstractparser import AbstractParser
import struct

class sdMainboardParser(AbstractParser):
    """
    Parser for ultrasonic sensor data.
    """
    def __init__(self):
        self.parser=struct.Struct("<BxxxI")

    @staticmethod
    def get_name() -> str:
        return "SD Mainboard"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp"]

    @staticmethod
    def get_data_length() -> int:
        return 8

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\x02')]  # Assuming the first byte is the ID for SD Mainboard

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, timestamp = self.parser.unpack(data)
        return {
            "timestamp": timestamp
        }

parser = sdMainboardParser()