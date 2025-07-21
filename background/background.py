from queue import Queue
import threading

from background.parsermanager import ParserManager
import shared_data

class Background:
    """
    Background processing tasks.
    """
    def __init__(self, data_queue: Queue):
        self.data_queue = data_queue
        self.parser_manager = ParserManager()

    def get_parser_names(self) -> list[str]:
        """
        Returns a list of available parser names.
        """
        return self.parser_manager.get_parser_names()

    def get_parser_information(self, parsername: str) -> dict:
        """
        Returns information about a specific parser.
        """
        return self.parser_manager.get_parser_information(parsername)

    def latest_data_dict(self, queue: Queue):
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
                parsed_data, parser_name = self.parser_manager.parse_data(data[0])
                print(f"Parsed data: {parsed_data}, Parser name: {parser_name}")
                if parser_name is None:
                    print("No parser found for the data.")
                else:
                    parsed_data["received_time"] = data[1]  # Use the received time from the queue
                    with shared_data.data_lock:
                        shared_data.data_dict[parser_name] = parsed_data  # Assuming data is a tuple (parsed_data, parser_name)
            else:
                threading.Event().wait(0.05)  # Wait for 0.05 seconds before checking again

    def get_background_thread(self, queue: Queue) -> threading.Thread:
        """
        Returns a thread that runs the latest_data_dict function.
        """
        return threading.Thread(target=self.latest_data_dict, args=(queue,), daemon=True)
