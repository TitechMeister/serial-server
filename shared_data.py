"""
# shared_data.py
This module contains shared data structures and state management for the serial server.
It is used for thread-safe access to data and serial connection state.
"""
import threading
from enum import Enum, auto

# Shared data and lock for thread-safe access (between background threads and HTTP server)
data_lock = threading.Lock()
data_dict = {}

# State management for the serial connection (between serial handler and HTTP server)
state_lock = threading.Lock()
class SerialState(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()
    READING = auto()
    ERROR = auto()
serial_state = SerialState.DISCONNECTED

# File path for logging
log_raw_file_path = "mainlog.txt"
log_processed_file_path = "processedlog.txt"