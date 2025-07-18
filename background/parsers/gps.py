from background.abstractparser import AbstractParser
import struct

class GPSParser(AbstractParser):
    """
    Parser for ultrasonic sensor data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BBHHxxIIIIIIIII")

    @staticmethod
    def get_name() -> str:
        return "gps"

    @staticmethod
    def get_keys() -> list[str]:
        return ["fixmode", "PDOP", "year","iTow", "timestamp", "longitude", "latitude", "height", "hAcc", "vAcc", "gspeed", "headMotion"]

    @staticmethod
    def get_data_length() -> int:
        return 44

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\x60')]  # Assuming the first byte is the ID for ultrasonic sensor

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, fixmode, PDOP, year, iTow, timestamp, longitude, latitude, height, hAcc, vAcc, gspeed, headMotion = self.parser.unpack(data)
        return {
            "fixmode": fixmode,
            "PDOP": PDOP,
            "year": year,
            "iTow": iTow,
            "timestamp": timestamp,
            "longitude": longitude,
            "latitude": latitude,
            "height": height,
            "hAcc": hAcc,
            "vAcc": vAcc,
            "gspeed": gspeed,
            "headMotion": headMotion
        }

parser = GPSParser()