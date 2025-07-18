import sys
import os

# Add the parent directory to sys.path to import lib.cobs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import background.abstractparser as abstractparser

def test_abstract_parser():
    pass