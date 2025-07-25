from background.abstractparser import AbstractParser
import struct

class HumidityAndTemperatureParser(AbstractParser):
    """
    Parser for humidity and temperature sensor data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BxxxIff")

    @staticmethod
    def get_name() -> str:
        return "humidity_and_temperature"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "humidity", "temperature"]

    @staticmethod
    def get_data_length() -> int:
        return 16

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\xB0')]  # Assuming the first byte is the ID for humidity and temperature sensor

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, timestamp, humidity, temperature = self.parser.unpack(data)
        return {
            "timestamp": timestamp,
            "humidity": humidity,
            "temperature": temperature
        }

parser = HumidityAndTemperatureParser()