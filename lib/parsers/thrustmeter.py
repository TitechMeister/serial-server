import tachometer

class ThrustmeterParser(tachometer.StrainAndCadenceParser):
    """
    Parser for thrustmeter sensor data.
    """
    @staticmethod
    def get_name() -> str:
        return "Thrustmeter"

    @staticmethod
    def get_id_bytes() -> list[(int, bytes)]:
        return [(0, b'\x21')]  # Assuming the first byte is the ID for thrustmeter sensor

parser = ThrustmeterParser()