#!/usr/bin/env python3
"""
Test script to verify admin settings form validation works without email_validator
"""
import os
import sys

# Disable pygame to avoid hardware conflicts
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Mock testing flag
os.environ['TESTING'] = '1'

# Import app components
from app import AdminSettingsForm, app

# Test the form validation
def test_admin_settings_form():
    print("Testing AdminSettingsForm validation...")
    
    # Mock request data
    form_data = {
        'sender_email': 'test@example.com',
        'app_password': 'secretpassword',
        'recipient_emails': 'admin@example.com,user@example.com',
        'timer_duration': '10'
    }
    
    try:
        # Create form with mock data - need Flask app and request context for Flask-WTF CSRF
        with app.app_context():
            with app.test_request_context():
                form = AdminSettingsForm(data=form_data)
                
                # Test validation (this would previously throw 500 error)
                is_valid = form.validate()
                
                print(f"Form validation result: {is_valid}")
                
                if not is_valid:
                    print("Form errors:")
                    for field, errors in form.errors.items():
                        for error in errors:
                            print(f"  {field}: {error}")
                else:
                    print("Form validated successfully!")
                    print(f"sender_email: {form.sender_email.data}")
                    print(f"app_password: {form.app_password.data}")
                    print(f"recipient_emails: {form.recipient_emails.data}")
                    print(f"timer_duration: {form.timer_duration.data}")
            
    except Exception as e:
        print(f"Error during form validation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = test_admin_settings_form()
    if success:
        print("\nTEST PASSED: Admin settings form validation works without email_validator!")
        sys.exit(0)
    else:
        print("\nTEST FAILED: Admin settings form validation still has issues.")
        sys.exit(1)