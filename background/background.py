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
        log_count = 0
        with open(shared_data.log_raw_file_path, "a") as log_file:
            with open(shared_data.log_processed_file_path, "a") as processed_log_file:
                while True:
                    while not queue.empty():
                        data = queue.get()
                        if data == (None, None):
                            print("connection closed")
                            continue
                        print(f"Latest data: {data}")
                        log_file.write(f"{data[1]}, {data[0].hex()}\n")
                        parsed_data, parser_name = self.parser_manager.parse_data(data[0])
                        print(f"Parsed data: {parsed_data}, Parser name: {parser_name}")
                        if parser_name is None:
                            print("No parser found for the data.")
                        else:
                            parsed_data["received_time"] = data[1]  # Use the received time from the queue
                            processed_log_file.write(f"{parser_name}, {parsed_data}\n")
                            with shared_data.data_lock:
                                shared_data.data_dict[parser_name] = parsed_data  # Assuming data is a tuple (parsed_data, parser_name)

                        log_count += 1
                        if log_count >= 20:
                            log_file.flush()
                            processed_log_file.flush()
                            log_count = 0
                    else:
                        threading.Event().wait(0.05)  # Wait for 0.05 seconds before checking again

        print("Background thread stopped.")

    def get_background_thread(self, queue: Queue) -> threading.Thread:
        """
        Returns a thread that runs the latest_data_dict function.
        """
        return threading.Thread(target=self.latest_data_dict, args=(queue,), daemon=True)
