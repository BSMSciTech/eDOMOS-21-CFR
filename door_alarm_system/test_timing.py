#!/usr/bin/env python3
"""
Test timing accuracy of alarm system
"""
import time
import os
import sys

# Set testing mode to avoid GPIO operations
os.environ['TESTING'] = '1'

def test_basic_timing():
    """Test basic timing accuracy"""
    print("Testing basic timing accuracy...")
    
    durations_to_test = [3, 5, 7, 10]
    
    for duration in durations_to_test:
        print(f"\nTesting {duration} second timer:")
        start_time = time.time()
        
        # Simple countdown loop similar to alarm_timer
        while (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            remaining = duration - elapsed
            if int(elapsed) % 1 == 0 and elapsed > 0:  # Every second
                print(f"  Elapsed: {elapsed:.1f}s, Remaining: {remaining:.1f}s")
            time.sleep(0.1)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        print(f"  Expected: {duration}s, Actual: {actual_duration:.2f}s, Diff: {actual_duration - duration:.2f}s")

if __name__ == "__main__":
    test_basic_timing()
