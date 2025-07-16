from lib.abstractparser import AbstractParser
import struct

class PitotParser(AbstractParser):
    """
    Parser for pitot sensor data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BxxxIfffff")

    @staticmethod
    def get_name() -> str:
        return "Pitot"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "temperature", "velocity", "pressure_velocity", "pressure_attack", "pressure_slip"]

    @staticmethod
    def get_data_length() -> int:
        return 28

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\x30')]  # Assuming the first byte is the ID for pitot sensor

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, timestamp, temperature, velocity, pressure_velocity, pressure_attack, pressure_slip = self.parser.unpack(data)
        return {
            "timestamp": timestamp,
            "temperature": temperature,
            "velocity": velocity,
            "pressure_velocity": pressure_velocity,
            "pressure_attack": pressure_attack,
            "pressure_slip": pressure_slip
        }

parser = PitotParser()