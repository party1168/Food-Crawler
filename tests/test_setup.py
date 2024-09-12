# test_setup.py
import sys
import os

def setup_test_env():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(parent_dir)

setup_test_env()