#!/usr/bin/env python3
"""
Quick test to verify admin settings form works without email_validator
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set testing mode to avoid GPIO initialization
os.environ['TESTING'] = 'true'

from app import app, db
from werkzeug.test import Client
from werkzeug.serving import WSGIRequestHandler

def test_admin_settings():
    """Test admin settings form submission"""
    with app.app_context():
        # Create test client
        client = app.test_client()
        
        # First login as admin (assuming admin user exists)
        login_response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'  # Default admin password
        })
        
        print(f"Login response status: {login_response.status_code}")
        
        # Test admin settings form
        admin_response = client.post('/admin/settings', data={
            'timer_duration': '10',
            'email_enabled': 'y',
            'email_host': 'smtp.gmail.com',
            'email_port': '587',
            'email_username': 'test@gmail.com',
            'email_password': 'testpass',
            'email_from': 'alarm@mydomain.com',
            'email_to': 'admin@mydomain.com'
        })
        
        print(f"Admin settings response status: {admin_response.status_code}")
        
        if admin_response.status_code == 500:
            print("❌ Still getting 500 error")
            print(admin_response.get_data(as_text=True))
        elif admin_response.status_code in [200, 302]:
            print("✅ Admin settings form working correctly!")
        else:
            print(f"Unexpected status code: {admin_response.status_code}")

if __name__ == '__main__':
    test_admin_settings()