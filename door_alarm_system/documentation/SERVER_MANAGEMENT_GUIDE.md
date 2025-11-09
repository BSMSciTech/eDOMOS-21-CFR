# eDOMOS Server Management - COMPLETE SOLUTION

## ✅ Problem Resolution Summary

### Issues Identified
1. **Port Already in Use**: Multiple instances of app.py running simultaneously
2. **GPIO Pins Busy**: Previous processes holding GPIO pins (pins 11, 13, 16, 18, 22)
3. **Incomplete Cleanup**: Simple `kill port 5000` wasn't releasing GPIO hardware
4. **Lingering nohup Processes**: Background processes surviving terminal closure

### Root Cause
The application uses hardware GPIO pins that **must be properly released** before a new instance can start. Simply killing the port doesn't release the GPIO pins, causing "GPIO busy" and "GPIO not allocated" errors.

---

## 🛠️ New Management Tools Created

### 1. **gpio_reset.py** - GPIO Hardware Reset
**Purpose**: Forcefully resets all GPIO pins to clean state

**Usage**:
```bash
python3 gpio_reset.py
```

**What it does**:
- Cleans up GPIO in BCM mode
- Cleans up GPIO in BOARD mode
- Force-cleans specific pins (11, 13, 16, 18, 22)
- Resets GPIO mode to BOARD
- Final comprehensive cleanup

---

### 2. **start.sh** - Comprehensive Startup Script
**Purpose**: Complete server startup with proper cleanup

**Usage**:
```bash
# Start with HTTP
./start.sh

# Start with HTTPS
USE_SSL=true ./start.sh
```

**What it does**:
1. **Process Cleanup**: Kills existing app.py processes
2. **Port Cleanup**: Clears port 5000
3. **GPIO Reset**: Runs gpio_reset.py
4. **Environment Verification**: Checks all requirements
5. **Server Startup**: Starts server with nohup
6. **PID Management**: Saves PID to /tmp/edomos.pid
7. **Startup Verification**: Confirms server is running

**Features**:
- Saves server PID for tracking
- Logs to /tmp/edomos_https.log
- Automatic SSL certificate detection
- Comprehensive status reporting

---

### 3. **stop.sh** - Enhanced Stop Script
**Purpose**: Gracefully stops server and cleans up

**Usage**:
```bash
./stop.sh
```

**What it does**:
1. **Graceful Shutdown**: Sends SIGTERM first
2. **Force Kill**: If graceful fails, uses SIGKILL
3. **Process Cleanup**: Removes all app.py processes
4. **Port Cleanup**: Clears port 5000
5. **PID File Cleanup**: Removes /tmp/edomos.pid
6. **Verification**: Confirms complete shutdown

---

## 📋 Complete Workflow

### Starting the Server

```bash
cd /home/bsm/WebApp/eDOMOS-v2.1/door_alarm_system

# For HTTPS (recommended)
USE_SSL=true ./start.sh

# For HTTP
./start.sh
```

**Expected Output**:
```
============================================================
🚀 eDOMOS STARTUP SCRIPT
============================================================

[1/5] Checking for existing eDOMOS processes...
  └─ Port 5000 is free

[2/5] Resetting GPIO pins...
  ✅ GPIO RESET COMPLETE

[3/5] Verifying environment...
  ├─ app.py found ✓
  ├─ Python 3.13.5 ✓
  └─ Mode: HTTPS 🔐

[4/5] Starting eDOMOS server...
  ├─ Server PID: 41292
  └─ Log file: /tmp/edomos_https.log

[5/5] Verifying server startup...
  ├─ Process is running ✓
  ├─ Port 5000 is listening ✓

✅ eDOMOS SERVER STARTED SUCCESSFULLY

📋 Server Information:
  ├─ PID: 41292
  ├─ URL: https://192.168.31.227:5000
  ├─ Mode: HTTPS (Secure) 🔐
```

---

### Stopping the Server

```bash
./stop.sh
```

**Expected Output**:
```
============================================================
🛑 STOPPING eDOMOS SERVER
============================================================

[1/3] Stopping server processes...
  ├─ Found server PID from file: 41292
  ├─ Process stopped gracefully ✓

[2/3] Clearing port 5000...
  └─ Port 5000 is already free ✓

[3/3] Verifying shutdown...
  ├─ No app.py processes running ✓
  └─ Port 5000 is free ✓

✅ eDOMOS SERVER STOPPED
```

---

### Checking Server Status

```bash
# View live logs
tail -f /tmp/edomos_https.log

# Check if server is running
ps aux | grep app.py

# Check port 5000
sudo lsof -i:5000

# Check GPIO pins
ls -la /dev/gpiomem
```

---

## 🔍 Troubleshooting Guide

### Issue: "Port already in use"

**Solution 1 (Recommended)**: Use stop script
```bash
./stop.sh
```

**Solution 2**: Manual cleanup
```bash
sudo lsof -ti:5000 | xargs -r sudo kill -9
```

---

### Issue: "GPIO busy" or "GPIO not allocated"

**Solution 1 (Recommended)**: Use start script (includes GPIO reset)
```bash
USE_SSL=true ./start.sh
```

**Solution 2**: Manual GPIO reset
```bash
python3 gpio_reset.py
```

**Solution 3**: Kill processes using GPIO
```bash
sudo fuser -k /dev/gpiomem
```

---

### Issue: Server starts but dies immediately

**Check logs**:
```bash
tail -50 /tmp/edomos_https.log
```

**Common causes**:
1. Database corruption → Delete `instance/alarm_system.db`
2. Missing SSL certificates → Use HTTP mode or regenerate certs
3. Permission issues → Check file ownership
4. Python package issues → Reinstall requirements

---

### Issue: Can't access server in browser

**Check network**:
```bash
# Verify server is listening
sudo lsof -i:5000

# Test locally
curl -k https://192.168.31.227:5000/api/test/ping

# Check firewall
sudo ufw status
```

---

## 📁 Important Files

| File | Purpose | Location |
|------|---------|----------|
| **app.py** | Main application | `door_alarm_system/app.py` |
| **start.sh** | Startup script | `door_alarm_system/start.sh` |
| **stop.sh** | Stop script | `door_alarm_system/stop.sh` |
| **gpio_reset.py** | GPIO reset utility | `door_alarm_system/gpio_reset.py` |
| **PID file** | Current process ID | `/tmp/edomos.pid` |
| **Log file** | Server logs | `/tmp/edomos_https.log` |
| **Database** | Event storage | `instance/alarm_system.db` |
| **SSL certs** | HTTPS certificates | `ssl/cert.pem`, `ssl/key.pem` |

---

## 🎯 Current Server Status

✅ **Server Running Successfully**
- PID: 41292
- URL: https://192.168.31.227:5000
- Mode: HTTPS (Secure) 🔐
- GPIO Pins: All 5 pins initialized ✓
- Port 5000: Listening ✓

**GPIO Status**:
```
✅ Pin 11: Magnetic sensor (Door sensor)
✅ Pin 22: Green LED (Status indicator)
✅ Pin 13: Red LED (Alarm indicator)
✅ Pin 16: White LED (Timer indicator)
✅ Pin 18: Switch (Manual control)
```

---

## 🚀 Quick Commands Reference

```bash
# Start server (HTTPS)
USE_SSL=true ./start.sh

# Start server (HTTP)
./start.sh

# Stop server
./stop.sh

# Restart server (HTTPS)
./stop.sh && sleep 2 && USE_SSL=true ./start.sh

# View logs
tail -f /tmp/edomos_https.log

# Check status
ps aux | grep app.py
sudo lsof -i:5000

# Reset GPIO (if needed)
python3 gpio_reset.py

# Kill port 5000 (emergency)
sudo lsof -ti:5000 | xargs -r sudo kill -9

# Access server
# Browser: https://192.168.31.227:5000
# Login: admin / admin123
```

---

## 💡 Key Improvements Made

1. ✅ **Automated GPIO Reset**: No more manual pin cleanup
2. ✅ **PID File Management**: Track server process reliably
3. ✅ **Graceful Shutdown**: Proper SIGTERM before SIGKILL
4. ✅ **Comprehensive Logging**: Better debugging information
5. ✅ **Status Verification**: Confirm startup success
6. ✅ **Environment Checks**: Verify requirements before starting
7. ✅ **SSL Auto-Detection**: Automatic HTTPS/HTTP mode selection
8. ✅ **Process Isolation**: Prevent multiple instances

---

## 📝 Notes

- **Always use `./start.sh`** instead of `python app.py` directly
- **GPIO reset** is now automatic during startup
- **PID tracking** prevents orphaned processes
- **nohup logs** are centralized in `/tmp/edomos_https.log`
- **Root CA certificate** is already installed for browser trust

---

## ✨ Success!

The server is now running properly with:
- ✅ All GPIO pins initialized
- ✅ Port 5000 listening
- ✅ HTTPS/SSL enabled
- ✅ No conflicting processes
- ✅ Clean startup and shutdown

**No more repeated "port already in use" or "GPIO busy" errors!**

---

*Generated: October 23, 2025*  
*eDOMOS v2.1 - Door Alarm System*
