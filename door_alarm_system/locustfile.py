"""
Locust Load Testing for eDOMOS
==============================
Performance and stress testing for industrial pharmaceutical systems

Usage:
    locust -f locustfile.py --host=http://localhost:5000
    locust -f locustfile.py --host=https://your-server.com --users 50 --spawn-rate 5
"""

from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime


class eDOMOSUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    def on_start(self):
        """Login when user starts"""
        self.login()
    
    def login(self):
        """Perform login and maintain session"""
        response = self.client.post("/login", data={
            "username": "testadmin",
            "password": "TestAdmin123!"
        }, name="/login")
        
        if response.status_code != 200:
            print(f"⚠️ Login failed with status {response.status_code}")
        else:
            print(f"✅ User logged in successfully")
    
    @task(10)
    def view_dashboard(self):
        """View main dashboard (most common action)"""
        with self.client.get("/dashboard", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Dashboard returned {response.status_code}")
    
    @task(8)
    def get_dashboard_api(self):
        """Get dashboard stats via API"""
        with self.client.get("/api/dashboard", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                try:
                    if response.status_code == 200:
                        data = response.json()
                    response.success()
                except (json.JSONDecodeError, ValueError):
                    # 404 returns HTML, not JSON - that's OK
                    response.success()
            else:
                response.failure(f"API returned {response.status_code}")
    
    @task(6)
    def get_ai_stats(self):
        """Get AI statistics"""
        with self.client.get("/api/ai/stats", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"AI stats returned {response.status_code}")
    
    @task(5)
    def view_event_logs(self):
        """View event logs"""
        with self.client.get("/logs", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Logs returned {response.status_code}")
    
    @task(4)
    def view_reports(self):
        """View reports section"""
        with self.client.get("/reports", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Reports returned {response.status_code}")
    
    @task(3)
    def view_change_control(self):
        """View change control dashboard"""
        with self.client.get("/change-control", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Change control returned {response.status_code}")
    
    @task(3)
    def view_validation(self):
        """View validation dashboard"""
        with self.client.get("/validation", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Validation returned {response.status_code}")
    
    @task(2)
    def view_training(self):
        """View training modules"""
        with self.client.get("/training", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Training returned {response.status_code}")
    
    @task(2)
    def view_settings(self):
        """View settings page"""
        with self.client.get("/settings", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Settings returned {response.status_code}")
    
    @task(1)
    def create_change_request(self):
        """Create a change request (less frequent)"""
        data = {
            "title": f"Load Test Change {random.randint(1000, 9999)}",
            "description": "Automated load testing change request",
            "category": random.choice(['system', 'procedure', 'documentation']),
            "priority": random.choice(['low', 'medium', 'high']),
            "reason": "Load testing"
        }
        
        with self.client.post("/change-control/request/create", 
                             data=data, 
                             catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Create change returned {response.status_code}")


class AdminUser(eDOMOSUser):
    """Heavy admin user performing administrative tasks"""
    
    weight = 1  # 1 admin for every 10 regular users
    
    @task(5)
    def manage_users(self):
        """Manage user accounts"""
        with self.client.get("/admin/users", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"User management returned {response.status_code}")
    
    @task(3)
    def export_reports(self):
        """Export PDF reports"""
        with self.client.get("/reports/export/pdf", catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"PDF export returned {response.status_code}")
    
    @task(2)
    def system_backup(self):
        """Trigger system backup"""
        with self.client.post("/admin/backup", catch_response=True) as response:
            if response.status_code in [200, 404, 500]:
                response.success()
            else:
                response.failure(f"Backup returned {response.status_code}")


class ValidationUser(eDOMOSUser):
    """User focused on validation tasks"""
    
    weight = 2  # 2 validation users for every 10 regular users
    
    @task(8)
    def view_validation_tests(self):
        """View validation tests"""
        with self.client.get("/validation/tests", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Validation tests returned {response.status_code}")
    
    @task(5)
    def export_iq_template(self):
        """Export IQ template"""
        with self.client.get("/validation/export/iq-template", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"IQ template export failed with {response.status_code}")
    
    @task(3)
    def view_validation_documents(self):
        """View validation documents"""
        with self.client.get("/validation/documents", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Validation docs returned {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("\n" + "="*60)
    print("🔬 eDOMOS INDUSTRIAL LOAD TEST STARTING")
    print("="*60)
    print(f"Target: {environment.host}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "="*60)
    print("✅ eDOMOS LOAD TEST COMPLETED")
    print("="*60)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests"""
    if response_time > 2000:  # Requests slower than 2 seconds
        print(f"⚠️  SLOW REQUEST: {name} took {response_time}ms")
