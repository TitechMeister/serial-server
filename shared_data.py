import threading

# Shared data and lock for thread-safe access
data_lock = threading.Lock()
data_dict = {}
