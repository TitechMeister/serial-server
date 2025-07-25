import bisect
import numpy as np
from background.abstractparser import AbstractParser
import struct

class ServoControllerParser(AbstractParser):
    """
    Parser for servo controller data.
    """
    def __init__(self):
        self.parser=struct.Struct(">BBxxIffffffffff")
        self.rudder_wing2servo = lambda x: 1.12e-4*x**4 + 5.84e-3*x**3 + -0.0205*x**2 + 4.21*x + 4.39 + 180
        self.elevator_wing2servo = lambda x: -1.49e-3*x**4 + -0.0401*x**3 + -0.267*x**2 + -6.07*x + -47.1 + 180
        self.list_r = [(self.rudder_wing2servo(i), i) for i in np.arange(-20, 20, 0.01)]
        self.list_e = [(self.elevator_wing2servo(i), i) for i in np.arange(-20, 20, 0.01)]
        # サーボの角度順にソート
        self.list_r.sort(key=lambda x: x[0])
        self.list_e.sort(key=lambda x: x[0])
        # bisect用にサーボの角度のみのリストを作成
        self.list_r_servo = [angle for angle, _ in self.list_r]
        self.list_e_servo = [angle for angle, _ in self.list_e] 
        

    @staticmethod
    def get_name() -> str:
        return "servocontroller"

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

    def _rudder_servo_to_wing_angle(self, servo_angle: float) -> float:
        left = bisect.bisect_left(self.list_r_servo, servo_angle)
        return round(self.list_r[left][1], 2)   # np.float64の小数点がきれいに表示されないため、roundで小数点以下2桁に丸める

    def _elevator_servo_to_wing_angle(self, servo_angle: float) -> float:
        left = bisect.bisect_left(self.list_e_servo, servo_angle)
        return round(self.list_e[left][1], 2)

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
            "pos_rudder_wing": self._rudder_servo_to_wing_angle(pos_rudder),  # Placeholder for wing position
            "pos_elevator_wing": self._elevator_servo_to_wing_angle(pos_elevator)  # Placeholder for wing position
        }
        
parser = ServoControllerParser()