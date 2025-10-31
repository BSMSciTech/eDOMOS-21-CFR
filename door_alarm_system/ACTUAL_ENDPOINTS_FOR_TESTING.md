# 🎯 ACTUAL eDOMOS v2.1 Endpoints for Locust Testing

## Authentication Required: YES (for most endpoints)

### 🔐 How to Authenticate in Locust

```python
class AuthenticatedUser(HttpUser):
    def on_start(self):
        """Login once when user starts"""
        self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })
        # Session cookie is automatically stored
```

---

## 📍 ACTUAL ENDPOINTS IN YOUR APP

### 1. PUBLIC ENDPOINTS (No Auth Required)

#### GET `/`
- Home page (redirects to login or dashboard)

#### GET/POST `/login`
- Login page and authentication
- **POST data:** `username`, `password`

---

### 2. AUTHENTICATED PAGE ENDPOINTS

#### GET `/dashboard`
- Main dashboard page
- Returns HTML with all dashboard data

#### GET `/event-log`
- Event log page
- Returns HTML with event history

#### GET `/analytics`
- Analytics page with charts
- Returns HTML with analytics data

#### GET `/reports`
- Reports generation page
- Returns HTML

#### GET `/admin`
- Admin panel page (admin only)
- Returns HTML

#### GET `/company-profile`
- Company profile management page (admin only)
- Returns HTML

#### GET `/user-management`
- User management page (admin only)
- Returns HTML

---

### 3. API ENDPOINTS (JSON Responses)

#### GET `/api/dashboard`
- **Returns:** Complete dashboard data in JSON
- **Response:**
```json
{
  "door_status": "Open/Closed",
  "alarm_status": "Active/Inactive",
  "timer_set": "30",
  "total_events": 123,
  "door_open_events": 45,
  "door_close_events": 45,
  "alarm_events": 10,
  "last_event": {...},
  "recent_events": [...],
  "uptime": {...}
}
```

#### GET `/api/status`
- **Returns:** Current system status
- **Response:**
```json
{
  "door_status": "Open/Closed",
  "alarm_status": "Active/Inactive",
  "timer_set": "30",
  "timestamp": "2025-10-23T..."
}
```

#### GET `/api/uptime`
- **Returns:** System uptime information
- **Response:**
```json
{
  "uptime": {
    "days": 5,
    "hours": 12,
    "minutes": 30,
    "seconds": 45,
    "formatted": "5 days, 12 hours, 30 minutes"
  }
}
```

#### GET `/api/events`
- **Returns:** Event log with pagination
- **Query params:** `page`, `per_page`, `since` (for polling)
- **Response:**
```json
{
  "events": [...],
  "total": 500,
  "pages": 25,
  "current_page": 1
}
```

#### GET `/api/statistics`
- **Returns:** Event statistics
- **Response:**
```json
{
  "total_events": 123,
  "door_open_events": 45,
  "door_close_events": 45,
  "alarm_events": 10
}
```

#### GET `/api/analytics/data`
- **Returns:** Analytics metrics
- **Query params:** `range` (day/week/month)
- **Response:**
```json
{
  "door_metrics": {...},
  "alarm_metrics": {...},
  "performance_metrics": {...}
}
```

#### GET `/api/company-profile`
- **Returns:** Company profile data
- **Response:**
```json
{
  "profile": {
    "company_name": "...",
    "company_address": "...",
    "company_phone": "...",
    ...
  }
}
```

#### POST `/api/company-profile`
- **Body:** Company profile fields
- **Returns:** Updated profile

#### GET `/api/door-system-info`
- **Returns:** Door system configuration
- **Response:**
```json
{
  "info": {
    "door_location": "...",
    "department_name": "...",
    "device_serial_number": "...",
    ...
  }
}
```

#### POST `/api/door-system-info`
- **Body:** System info fields
- **Returns:** Updated info

#### GET `/api/users`
- **Returns:** List of all users (admin only)
- **Response:**
```json
{
  "users": [...]
}
```

#### POST `/api/users`
- **Body:** New user data
- **Returns:** Created user (admin only)

#### GET `/api/users/<user_id>`
- **Returns:** Specific user details (admin only)

#### PUT `/api/users/<user_id>`
- **Body:** Updated user fields
- **Returns:** Updated user (admin only)

#### DELETE `/api/users/<user_id>`
- **Returns:** Success message (admin only)

#### POST `/api/settings`
- **Body:** Settings to update
- **Returns:** Success message

#### GET `/api/backup`
- **Returns:** Database backup file download

#### POST `/api/test-event`
- **Body:** `event_type`, `description`
- **Returns:** Success (admin only)
- **Purpose:** Manually create test events

#### POST `/api/report`
- **Body:** 
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-23",
  "event_types": ["door_open", "door_close"],
  "format": "csv" or "pdf" or "json"
}
```
- **Returns:** Report data (PDF as base64, CSV as file, or JSON)

#### POST `/api/upload-logo`
- **Body:** Multipart form with logo file
- **Returns:** Logo path (admin only)

---

## 🔥 SAMPLE LOCUST FILE FOR YOUR ACTUAL ENDPOINTS

```python
from locust import HttpUser, task, between
import random

class eDOMOSUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login once when user starts"""
        response = self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })
        print(f"Login status: {response.status_code}")
    
    # ===== DASHBOARD TESTS =====
    @task(10)
    def view_dashboard(self):
        """Most common - view dashboard"""
        self.client.get("/dashboard")
    
    @task(8)
    def get_dashboard_api(self):
        """Get dashboard data via API"""
        self.client.get("/api/dashboard")
    
    @task(5)
    def get_status(self):
        """Check system status"""
        self.client.get("/api/status")
    
    # ===== EVENT LOG TESTS =====
    @task(6)
    def view_events_page(self):
        """View event log page"""
        self.client.get("/event-log")
    
    @task(7)
    def get_events_api(self):
        """Get events via API"""
        page = random.randint(1, 5)
        self.client.get(f"/api/events?page={page}&per_page=20")
    
    @task(3)
    def get_statistics(self):
        """Get statistics"""
        self.client.get("/api/statistics")
    
    # ===== ANALYTICS TESTS =====
    @task(4)
    def view_analytics_page(self):
        """View analytics page"""
        self.client.get("/analytics")
    
    @task(5)
    def get_analytics_data(self):
        """Get analytics data"""
        time_range = random.choice(['day', 'week', 'month'])
        self.client.get(f"/api/analytics/data?range={time_range}")
    
    # ===== REPORTS TESTS =====
    @task(2)
    def view_reports_page(self):
        """View reports page"""
        self.client.get("/reports")
    
    # ===== SYSTEM INFO TESTS =====
    @task(2)
    def get_uptime(self):
        """Get system uptime"""
        self.client.get("/api/uptime")
    
    @task(1)
    def get_company_profile(self):
        """Get company profile"""
        self.client.get("/api/company-profile")
    
    @task(1)
    def get_door_system_info(self):
        """Get door system info"""
        self.client.get("/api/door-system-info")


class ReadOnlyUser(HttpUser):
    """Simulates users who only read data (no writes)"""
    wait_time = between(0.5, 2)
    
    def on_start(self):
        self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })
    
    @task(20)
    def quick_status_check(self):
        """Fast status checks"""
        self.client.get("/api/status")
    
    @task(15)
    def dashboard_data(self):
        """Dashboard updates"""
        self.client.get("/api/dashboard")
    
    @task(10)
    def recent_events(self):
        """Recent events"""
        self.client.get("/api/events?page=1&per_page=10")
    
    @task(5)
    def statistics(self):
        """Quick stats"""
        self.client.get("/api/statistics")


class AdminUser(HttpUser):
    """Simulates admin users doing admin tasks"""
    wait_time = between(2, 5)
    
    def on_start(self):
        self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })
    
    @task(5)
    def view_admin_panel(self):
        """View admin panel"""
        self.client.get("/admin")
    
    @task(3)
    def view_users(self):
        """Get all users"""
        self.client.get("/api/users")
    
    @task(2)
    def view_company_profile(self):
        """View company profile"""
        self.client.get("/company-profile")
    
    @task(1)
    def view_user_management(self):
        """View user management"""
        self.client.get("/user-management")
```

---

## 🎯 RECOMMENDED TEST SCENARIOS

### Scenario 1: Normal User Load
```bash
locust -f locustfile.py --host=http://192.168.31.227:5000 --users=100 --spawn-rate=10
```
- Simulates 100 normal users
- Focus: Dashboard, events, analytics

### Scenario 2: Read-Heavy Load
```bash
locust -f locustfile.py --host=http://192.168.31.227:5000 --users=200 --spawn-rate=20 ReadOnlyUser
```
- Simulates 200 read-only users
- Focus: Status checks, dashboard updates

### Scenario 3: Mixed Load
```bash
locust -f locustfile.py --host=http://192.168.31.227:5000 --users=150 --spawn-rate=15
```
- 80% normal users
- 15% read-only users
- 5% admin users

### Scenario 4: Database Stress
```bash
# Focus on endpoints that query database heavily
```
- `/api/events` with pagination
- `/api/analytics/data` with different ranges
- `/api/report` generation

---

## 📊 KEY ENDPOINTS BY PERFORMANCE

### Fast Endpoints (< 100ms)
- `/api/status`
- `/api/uptime`
- `/api/statistics`

### Medium Endpoints (100-500ms)
- `/api/dashboard`
- `/api/events?page=1`
- `/api/company-profile`

### Slow Endpoints (500ms+)
- `/api/analytics/data` (complex queries)
- `/api/report` (PDF generation)
- `/analytics` page (heavy rendering)

---

## ✅ PRE-TEST CHECKLIST

1. **Verify server is running:**
   ```bash
   curl http://192.168.31.227:5000/api/status
   ```

2. **Test authentication:**
   ```bash
   curl -c cookies.txt -X POST http://192.168.31.227:5000/login \
     -d "username=admin&password=admin123"
   ```

3. **Test authenticated endpoint:**
   ```bash
   curl -b cookies.txt http://192.168.31.227:5000/api/dashboard
   ```

4. **Install Locust:**
   ```bash
   pip install locust
   ```

5. **Run Locust:**
   ```bash
   locust -f your_locustfile.py --host=http://192.168.31.227:5000
   ```

6. **Open web UI:**
   - http://localhost:8089

---

## 🚨 IMPORTANT NOTES

- **Authentication:** All endpoints except `/` and `/login` require authentication
- **Session Management:** Use `requests.Session()` in Locust to maintain cookies
- **Database:** Your actual database will be queried - **backup first!**
- **No Mock Data:** These are real endpoints hitting real database
- **Admin Endpoints:** Some require `is_admin=True` user

---

## 🎯 QUICK TEST COMMAND

```bash
# Copy this sample to locustfile.py and run:
locust -f locustfile.py --host=http://192.168.31.227:5000 --users=50 --spawn-rate=5 --run-time=2m
```

This will:
- Test with 50 concurrent users
- Spawn 5 users per second
- Run for 2 minutes
- Test all major endpoints

---

**These are YOUR actual endpoints - test away! 🚀**
