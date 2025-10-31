import requests
from requests.sessions import Session

session = Session()
login_page = session.get('http://localhost:5000/login')
print(f"Login page: {login_page.status_code}")

login_data = {'username': 'admin', 'password': 'admin123'}
login_response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
print(f"Login: {login_response.status_code}")

if login_response.status_code == 302:
    dashboard = session.get('http://localhost:5000/dashboard')
    print(f"Dashboard: {dashboard.status_code}")
    if dashboard.status_code == 200:
        print("✅ Successfully logged in and accessed dashboard!")
        print("🔗 You can now access: http://localhost:5000/dashboard")
