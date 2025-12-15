import os
import time
import requests

BOOKING_URL = os.getenv("BOOKING_URL", "http://localhost:8000")
CLEANING_URL = os.getenv("CLEANING_URL", "http://localhost:8001")

def _wait_ok(url: str, path: str, timeout_s: int = 60):
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        try:
            r = requests.get(url + path, timeout=3)
            if r.status_code == 200:
                return
            last = f"status={r.status_code}"
        except Exception as e:
            last = repr(e)
        time.sleep(2)
    raise AssertionError(f"{url+path} not ready: {last}")

def test_booking_openapi_ready():
    _wait_ok(BOOKING_URL, "/openapi.json")

def test_cleaning_openapi_ready():
    _wait_ok(CLEANING_URL, "/openapi.json")