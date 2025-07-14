from lib.abstractparser import AbstractParser
import struct

class ServoControllerParser(AbstractParser):
    """
    Parser for servo controller data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BBxxIffffffffff")

    @staticmethod
    def get_name() -> str:
        return "ServoController"

    @staticmethod
    def get_keys() -> list[str]:
        return ["timestamp", "rudder", "elevator", "voltage", "i_rudder", "i_elevator", "trim", "status", \
                "pos_rudder", "pos_elevator", "temp_rudder", "temp_elevator", "pos_rudder_wing", "pos_elevator_wing"]

    @staticmethod
    def get_data_length() -> int:
        return 48 

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\x10')]

    def parse(self, data: bytes) -> dict:
        _id,status,timestamp,rudder,elevator,voltage,i_rudder,i_elevator,trim,pos_rudder,pos_elevator,temp_rudder,temp_elevator=self.parser.unpack(data)

        return {
            "timestamp": timestamp,
            "rudder": rudder,
            "elevator": elevator,
            "voltage": voltage,
            "i_rudder": i_rudder,
            "i_elevator": i_elevator,
            "trim": trim,
            "status": status,
            "pos_rudder": pos_rudder,
            "pos_elevator": pos_elevator,
            "temp_rudder": temp_rudder,
            "temp_elevator": temp_elevator,
            "pos_rudder_wing": 0,  # Placeholder for wing position
            "pos_elevator_wing": 0  # Placeholder for wing position
        }
        
parser = ServoControllerParser()