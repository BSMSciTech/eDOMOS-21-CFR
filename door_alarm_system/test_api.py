import requests
import json

def test_api():
    print("Testing dashboard real-time API endpoints...")
    
    # Test if server is responding
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"Server responding: {response.status_code}")
        if response.status_code == 302:
            print("✅ Server is redirecting (login required) - this is expected")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

if __name__ == '__main__':
    test_api()
