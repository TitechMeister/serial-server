from background.abstractparser import AbstractParser
import struct

class PCSenderParser(AbstractParser):
    """
    Parser for humidity and temperature sensor data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BxxxIIIBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")

    @staticmethod
    def get_name() -> str:
        return "pcsender"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "target_longitude", "target_latitude", "additional_data"]

    @staticmethod
    def get_data_length() -> int:
        return 48

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\xE0')]  # Assuming the first byte is the ID for humidity and temperature sensor

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, timestamp, target_longitude, target_latitude, *additional_data = self.parser.unpack(data)
        return {
            "timestamp": timestamp,
            "target_longitude": target_longitude,
            "target_latitude": target_latitude,
            "additional_data": additional_data
        }

parser = PCSenderParser()