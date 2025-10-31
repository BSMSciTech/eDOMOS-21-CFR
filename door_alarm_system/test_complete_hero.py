#!/usr/bin/env python3
import requests
import time

def test_hero_door_status():
    BASE_URL = "http://localhost:5000"
    session = requests.Session()
    
    print("Testing Hero Section Door Status Updates")
    print("=" * 50)
    
    # Login
    print("1. Logging in...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if login_response.status_code in [200, 302]:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    # Test API
    print("2. Testing dashboard API...")
    api_response = session.get(f"{BASE_URL}/api/dashboard")
    
    if api_response.status_code == 200:
        try:
            data = api_response.json()
            print("✅ Dashboard API working")
            print(f"   Door Status: {data.get('door_status')}")
            print(f"   Total Events: {data.get('total_events')}")
        except:
            print(f"❌ API response not JSON: {api_response.text[:100]}")
            return False
    else:
        print(f"❌ API failed: {api_response.status_code}")
        print(f"   Response: {api_response.text[:200]}")
        return False
    
    # Test door events
    print("3. Testing door events...")
    
    # Door open event
    print("   Triggering door OPEN event...")
    door_open_data = {"event_type": "door_open", "description": "Test door open for hero section"}
    open_response = session.post(f"{BASE_URL}/api/test-event", json=door_open_data)
    print(f"   Open event response: {open_response.status_code}")
    time.sleep(1)
    
    status_response = session.get(f"{BASE_URL}/api/dashboard")
    if status_response.status_code == 200:
        try:
            status_data = status_response.json()
            print(f"   Status after open: {status_data.get('door_status')}")
        except:
            print("   ❌ Could not parse status response")
    
    time.sleep(2)
    
    # Door close event
    print("   Triggering door CLOSE event...")
    door_close_data = {"event_type": "door_close", "description": "Test door close for hero section"}
    close_response = session.post(f"{BASE_URL}/api/test-event", json=door_close_data)
    print(f"   Close event response: {close_response.status_code}")
    time.sleep(1)
    
    status_response = session.get(f"{BASE_URL}/api/dashboard")
    if status_response.status_code == 200:
        try:
            status_data = status_response.json()
            print(f"   Status after close: {status_data.get('door_status')}")
        except:
            print("   ❌ Could not parse status response")
    
    print("\n✅ Test completed! Check dashboard in browser for real-time updates.")
    return True

if __name__ == '__main__':
    test_hero_door_status()
