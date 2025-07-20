from background.abstractparser import AbstractParser
import struct

class BLEPowerMeterParser(AbstractParser):
    """
    Parser for power meter from pilot's cycle computer through BLE data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BxhId")

    @staticmethod
    def get_name() -> str:
        return "blepowermeter"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "power", "cadence"]

    @staticmethod
    def get_data_length() -> int:
        return 16

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\xA0')]  # Assuming the first byte is the ID for power meter

    def parse(self, data: bytes) -> dict:
        if len(data) != self.get_data_length():
            raise ValueError(f"Expected {self.get_data_length()} bytes, got {len(data)} bytes")

        _id, timestamp, power, cadence = self.parser.unpack(data)
        return {
            "timestamp": timestamp,
            "power": power,
            "cadence": cadence
        }

parser = BLEPowerMeterParser()