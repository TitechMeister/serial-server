from queue import Queue
import threading
import shared_data

def latest_data_dict(queue: Queue):
    """
    Continuously fetches the latest data from the queue.
    This function runs in a separate thread.
    """
    while True:
        if not queue.empty():
            data = queue.get()
            if data == (None, None):
                print("connection closed")
                return
            print(f"Latest data: {data}")
            with shared_data.data_lock:
                shared_data.data_dict[data[1]] = data[0]  # Assuming data is a tuple (parsed_data, parser_name)
        else:
            threading.Event().wait(0.05)  # Wait for 0.05 seconds before checking again

def get_background_thread(queue: Queue) -> threading.Thread:
    """
    Returns a thread that runs the latest_data_dict function.
    """
    return threading.Thread(target=latest_data_dict, args=(queue,), daemon=True)