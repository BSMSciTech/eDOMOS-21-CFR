#!/usr/bin/env python3
import requests
import time

print("Testing Hero Section Auto-Refresh")
print("=" * 40)

session = requests.Session()

# Login
login_data = {'username': 'admin', 'password': 'admin123'}
session.post('http://localhost:5000/login', data=login_data)
print("Logged in")

print("\nWatch the hero section in your browser!")
print("URL: http://localhost:5000/dashboard")

# Test door events
events = ['door_open', 'door_close', 'door_open', 'door_close']

for i, event in enumerate(events, 1):
    print(f"\n{i}. Triggering {event}...")
    
    # Trigger event
    response = session.post(f'http://localhost:5000/api/test-event', 
                           json={'event_type': event})
    
    if response.status_code == 200:
        print("✅ Event triggered")
        
        # Check status
        status_response = session.get('http://localhost:5000/api/dashboard')
        if status_response.status_code == 200:
            data = status_response.json()
            print(f"Door Status: {data.get('door_status')}")
        
    time.sleep(3)

print("\nTest complete! Hero section should have updated automatically.")
