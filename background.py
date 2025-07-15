from queue import Queue
import threading
from serialserver import data_lock, data_dict

def latest_data_dict(queue: Queue):
    """
    Continuously fetches the latest data from the queue.
    This function runs in a separate thread.
    """
    while True:
        if not queue.empty():
            data = queue.get()
            print(f"Latest data: {data}")
            with data_lock:
                data_dict[data[1]] = data[0]  # Assuming data is a tuple (parsed_data, parser_name)
        else:
            threading.Event().wait(0.05)  # Wait for 0.05 seconds before checking again