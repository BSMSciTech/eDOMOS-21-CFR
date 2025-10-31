#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/bsm/WebApp/eDOMOS-v2/eDOMOS-v2.1/door_alarm_system')

from app import app, db, Setting

def check_timer():
    with app.app_context():
        timer_setting = Setting.query.filter_by(key='timer_duration').first()
        if timer_setting:
            print(f"Timer Duration: {timer_setting.value} seconds")
        else:
            print("No timer setting found")
            # Create 7 second default
            new_setting = Setting(key='timer_duration', value='7')
            db.session.add(new_setting)
            db.session.commit()
            print("Created default 7 second timer")

if __name__ == "__main__":
    check_timer()
