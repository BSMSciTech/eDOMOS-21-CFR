# 🔥 Locust Load Testing Guide for eDOMOS v2.1

## 📋 Overview
This guide provides all the information needed to stress test the eDOMOS Door Alarm System using Locust from your client PC.

## 🚀 Quick Start

### 1. Get Available Endpoints
First, query the server to get all testable endpoints:

```bash
curl http://192.168.31.227:5000/api/test/endpoints
```

This returns a comprehensive JSON with:
- Public endpoints (no authentication)
- Authenticated endpoints (requires login)
- Testing tips and recommendations

---

## 🔓 Public Endpoints (No Authentication Required)

### Health Check
```python
@task(3)
def health_check(self):
    self.client.get("/api/test/health")
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-23T10:30:00",
  "uptime_seconds": 86400,
  "database": "ok",
  "gpio": "ok",
  "version": "2.1"
}
```

### Simple Ping
```python
@task(5)
def ping(self):
    self.client.get("/api/test/ping")
```

**Response:**
```json
{
  "ping": "pong",
  "timestamp": "2025-10-23T10:30:00"
}
```

### Mock Stress Data
```python
@task(2)
def stress_data(self):
    self.client.get("/api/test/stress-data")
```

**Response:** Returns mock data without database queries (for pure app server testing)

---

## 🔐 Authenticated Endpoints (Requires Login)

### Authentication Flow

#### Step 1: Login and Get Session Cookie
```python
class AuthenticatedUser(HttpUser):
    def on_start(self):
        """Login once when user starts"""
        response = self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })
        # Session cookie is automatically stored by requests.Session()
```

#### Step 2: Use Authenticated Endpoints
```python
@task(3)
def get_dashboard(self):
    self.client.get("/api/dashboard")

@task(2)
def get_status(self):
    self.client.get("/api/status")

@task(2)
def get_events(self):
    self.client.get("/api/events")
```

---

## 📝 Sample Locust File

```python
from locust import HttpUser, task, between

class eDOMOSUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login once when user starts"""
        self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })
    
    # Public endpoints (no auth needed)
    @task(5)
    def ping(self):
        """Simple ping test"""
        self.client.get("/api/test/ping")
    
    @task(3)
    def health_check(self):
        """Health check"""
        self.client.get("/api/test/health")
    
    @task(2)
    def stress_data(self):
        """Get mock data"""
        self.client.get("/api/test/stress-data")
    
    # Authenticated endpoints
    @task(4)
    def get_dashboard(self):
        """Dashboard data"""
        self.client.get("/api/dashboard")
    
    @task(3)
    def get_status(self):
        """System status"""
        self.client.get("/api/status")
    
    @task(3)
    def get_events(self):
        """Event log"""
        self.client.get("/api/events")
    
    @task(2)
    def get_statistics(self):
        """Statistics"""
        self.client.get("/api/statistics")
    
    @task(2)
    def get_uptime(self):
        """Uptime info"""
        self.client.get("/api/uptime")
    
    @task(1)
    def get_analytics(self):
        """Analytics data"""
        self.client.get("/api/analytics/data")
    
    @task(1)
    def get_company_profile(self):
        """Company profile"""
        self.client.get("/api/company-profile")


class UnauthenticatedUser(HttpUser):
    """Test public endpoints only (no login)"""
    wait_time = between(0.5, 2)
    
    @task(10)
    def ping(self):
        self.client.get("/api/test/ping")
    
    @task(5)
    def health_check(self):
        self.client.get("/api/test/health")
    
    @task(3)
    def stress_data(self):
        self.client.get("/api/test/stress-data")
```

---

## 🎯 Running Locust Tests

### From Your Client PC

1. **Install Locust:**
   ```bash
   pip install locust
   ```

2. **Create your locustfile.py** (use sample above)

3. **Run Locust:**
   ```bash
   locust -f locustfile.py --host=http://192.168.31.227:5000
   ```

4. **Open Web UI:**
   - Go to: http://localhost:8089
   - Set number of users (e.g., 100)
   - Set spawn rate (e.g., 10 users/second)
   - Click "Start Swarming"

---

## 📊 Recommended Test Scenarios

### Scenario 1: Public Endpoints Only
- **Users:** 500
- **Spawn Rate:** 50/sec
- **Endpoints:** `/api/test/ping`, `/api/test/health`
- **Goal:** Test raw server capacity

### Scenario 2: Authenticated Read Operations
- **Users:** 200
- **Spawn Rate:** 20/sec
- **Endpoints:** `/api/dashboard`, `/api/status`, `/api/events`
- **Goal:** Test real-world dashboard usage

### Scenario 3: Mixed Load
- **Users:** 300 (70% authenticated, 30% public)
- **Spawn Rate:** 30/sec
- **Endpoints:** Mix of all endpoints
- **Goal:** Simulate real production load

### Scenario 4: Database Stress
- **Users:** 100
- **Spawn Rate:** 10/sec
- **Endpoints:** `/api/events`, `/api/analytics/data`, `/api/statistics`
- **Goal:** Test database query performance

---

## 🔍 Key Metrics to Monitor

### Response Times
- **Excellent:** < 100ms
- **Good:** 100-500ms
- **Acceptable:** 500-1000ms
- **Poor:** > 1000ms

### Error Rates
- **Target:** < 1% errors
- **Acceptable:** < 5% errors
- **Critical:** > 10% errors

### Throughput
- **Goal:** > 100 requests/second
- **Optimal:** > 500 requests/second

---

## 🛠️ Troubleshooting

### Issue: 401 Unauthorized Errors
**Solution:** Make sure `on_start()` method logs in and session cookies are preserved

### Issue: Connection Refused
**Solution:** Check server is running: `curl http://192.168.31.227:5000/api/test/ping`

### Issue: Slow Response Times
**Solution:** 
- Reduce number of concurrent users
- Check server CPU/memory usage
- Use mock endpoint `/api/test/stress-data` to isolate database issues

### Issue: WebSocket Errors
**Solution:** WebSocket testing requires special Locust setup (use HTTP endpoints only)

---

## 📈 Performance Baselines (For Reference)

Based on Raspberry Pi 4 with 4GB RAM:

| Endpoint | Expected Response Time | Max Users |
|----------|----------------------|-----------|
| /api/test/ping | 10-50ms | 1000+ |
| /api/test/health | 50-150ms | 500+ |
| /api/status | 100-300ms | 300+ |
| /api/dashboard | 200-500ms | 200+ |
| /api/events | 300-800ms | 100+ |
| /api/analytics/data | 500-1500ms | 50+ |

---

## 🎯 Test Endpoints Summary

### Public (No Auth)
- ✅ `/api/test/endpoints` - Get all endpoints
- ✅ `/api/test/health` - Health check
- ✅ `/api/test/ping` - Simple ping
- ✅ `/api/test/stress-data` - Mock data

### Authenticated (Login Required)
- 🔐 `/api/test/auth-check` - Verify authentication
- 🔐 `/api/dashboard` - Dashboard data
- 🔐 `/api/status` - System status
- 🔐 `/api/uptime` - Uptime info
- 🔐 `/api/events` - Event log
- 🔐 `/api/statistics` - Statistics
- 🔐 `/api/analytics/data` - Analytics
- 🔐 `/api/company-profile` - Company info

---

## 🚀 Advanced: Custom Test Scenarios

### Test Event Log Filtering
```python
@task(2)
def search_events(self):
    params = {
        'search': 'door',
        'event_type': 'door_opened',
        'page': 1
    }
    self.client.get("/api/events", params=params)
```

### Test Date Range Queries
```python
@task(1)
def analytics_date_range(self):
    params = {
        'start_date': '2025-10-01',
        'end_date': '2025-10-23'
    }
    self.client.get("/api/analytics/data", params=params)
```

---

## 📞 Support

If you encounter issues:
1. Check server logs: `/home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system/app.py`
2. Verify endpoints: `curl http://192.168.31.227:5000/api/test/endpoints`
3. Test authentication: `curl http://192.168.31.227:5000/api/test/ping`

---

## ✅ Pre-Test Checklist

- [ ] Server is running: `curl http://192.168.31.227:5000/api/test/ping`
- [ ] Credentials work: `curl -X POST http://192.168.31.227:5000/login -d "username=admin&password=admin123"`
- [ ] Locust installed: `pip install locust`
- [ ] Network connectivity: Client PC can reach 192.168.31.227
- [ ] Monitoring ready: Terminal open to watch server logs
- [ ] Backup database: Copy `instance/door_alarm.db` before heavy testing

---

**Good Luck with Your Load Testing! 🚀**
