from abc import ABC, abstractmethod
import os
import pkgutil

class AbstractParser(ABC):
    """
    Abstract base class for data parsers.
    """
    @abstractmethod
    def parse(self, data: bytes) -> dict:
        """
        Parse the given byte data and return a dictionary of values.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """
        Return the name of the parser. (e.g., "Ultrasonic Sensor")
        """
        pass

    @staticmethod
    @abstractmethod
    def get_keys() -> list[str]:
        """
        Return a list of keys that the parser will return in the parsed data.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_id_bytes() -> list[(int, bytes)]:
        """
        Return a list of tuples mapping byte values to sensor IDs.
        This is used to identify the type of sensor from the data.
        Each tuple should be in the form (index, byte_value).

        The index is the position of the byte in the data, and
        byte_value is the expected byte value at that position.

        If continuous indexes, the byte_value can be a bytes object
        containing multiple bytes. In that case, the index will be
        the starting position of the byte sequence, and the byte_value
        will be a bytes object containing the expected byte values.

        For example, [(0, b'\x01'), (1, b'\x02\x03')] means that
        the first byte is 0x01 and the second byte is 0x02 and the third byte is 0x03
        """
        pass

    @staticmethod
    @abstractmethod
    def get_data_length() -> int:
        """
        Return the expected length of the data to be parsed.
        """
        pass


    
    def can_parse(self, data: bytes) -> bool:
        """
        Determine if the parser can handle the given data.
        """
        if len(data) == self.get_data_length():
            id_bytes = self.get_id_bytes()
            if id_bytes:
                for index, id_value in id_bytes:
                    if data[index:index + len(id_value)] != id_value:
                        return False  # Cannot parse
            return True  # Can parse

        return False  # Data length does not match expected length
