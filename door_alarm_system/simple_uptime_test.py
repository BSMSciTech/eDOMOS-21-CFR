#!/usr/bin/env python3
"""Simple uptime verification test"""

try:
    from app import calculate_uptime, SERVER_START_TIME
    from datetime import datetime
    
    print("🚀 eDOMOS v2.1 - Uptime System Test")
    print("=" * 50)
    print(f"Server Started: {SERVER_START_TIME}")
    print(f"Current Time:   {datetime.now()}")
    
    uptime = calculate_uptime()
    print(f"\n📊 Uptime Results:")
    print(f"  Display: {uptime['uptime_string']}")
    print(f"  Availability: {uptime['availability_percent']}%")
    print(f"  Total Seconds: {uptime['uptime_seconds']}")
    print(f"  Breakdown: {uptime['days']}d {uptime['hours']}h {uptime['minutes']}m {uptime['seconds']}s")
    
    print(f"\n✅ Uptime calculation system is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
