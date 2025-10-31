#!/usr/bin/env python3
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:5000"
auth = HTTPBasicAuth("admin", "admin123")

# Test dashboard API
response = requests.get(f"{BASE_URL}/api/dashboard", auth=auth)
if response.status_code == 200:
    data = response.json()
    door_status = data.get('door_status')
    print(f"Door Status: {door_status}")
    print(f"Total Events: {data.get('total_events')}")
else:
    print(f"API failed: {response.status_code}")
