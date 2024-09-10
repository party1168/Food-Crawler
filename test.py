# test_import.py
try:
    from utils.http_utils import make_request
    print("Successfully imported make_request from utils.http_utils")
except ImportError as e:
    print(f"Import failed: {e}")

try:
    from TastyOven_scraper import TastyOvenScraper
    print("Successfully imported TastyOvenScraper")
except ImportError as e:
    print(f"Import failed: {e}")