import sys
import os

# Add the parent directory to sys.path to import lib.cobs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
import background.parsermanager as parsermanager
import lib.cobs as cobs


def test_parser():
    myParsermanager = parsermanager.ParserManager()
    with open("main-log.bin", "rb") as f:
        data = f.read()
    index = 0
    while index < len(data):
        decoded_data, index = cobs.cobs_decode(data, index)
        decoded_data = bytes(decoded_data)
        print(f"Decoded data: {decoded_data.hex()}")
        if len(decoded_data) == 0:
            print("No data to parse, skipping...")
            continue
        parsed_data = myParsermanager.parse_data(decoded_data)
        print(f"Parsed data: {parsed_data}\n")