from lib.abstractparser import AbstractParser
from abc import abstractmethod
import struct

class StrainAndCadenceParser(AbstractParser):
    """
    Parser for strain and cadence sensor data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BxxxIdIxxxx")

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        pass

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "rps", "strain"]

    @staticmethod
    def get_data_length() -> int:
        return 24

    @staticmethod
    @abstractmethod
    def get_id_bytes() -> list[(int, bytes)]:
        pass

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, timestamp, rps, strain = self.parser.unpack(data)
        return {
            "timestamp": timestamp,
            "rps": rps,
            "strain": strain
        }

class TachometerParser(StrainAndCadenceParser):
    """
    Parser for tachometer sensor data.
    """
    @staticmethod
    def get_name() -> str:
        return "Tachometer"

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\x20')]  # Assuming the first byte is the ID for tachometer sensor

parser = TachometerParser()