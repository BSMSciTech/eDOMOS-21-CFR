import os
import time
import threading
import sqlite3
import json
import smtplib
import traceback
import csv
import base64
import signal
import atexit
import hashlib
import pygame  # For audio alarm functionality
import RPi.GPIO as GPIO
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, flash, render_template_string
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO, emit
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, ValidationError
import re

# Resilient email validator: prefer email_validator package but fallback to regex
def resilient_email(form, field):
    """Validate email addresses using email_validator when available, otherwise use simple regex."""
    try:
        import email_validator
        # Use WTForms Email validator behavior by importing and calling it
        from wtforms.validators import Email as WTEmail
        validator = WTEmail()
        validator(form, field)
    except Exception:
        # fallback basic regex (not RFC perfect but practical)
        email = field.data or ''
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, email):
            raise ValidationError('Invalid email address')
from sqlalchemy import func
from models import db, User, Setting, EventLog, EmailConfig, CompanyProfile, DoorSystemInfo, AnomalyDetection, ScheduledReport
from config import Config

# Initialize camera module
from camera_helper import initialize_camera_manager, capture_event_image

# Track server start time for uptime calculation
SERVER_START_TIME = datetime.now()

# Audio configuration
BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"
AUDIO_PATH = STATIC_DIR / "audio.mp3"

# Preloaded audio for instant playback
preloaded_sound = None

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'alarm_system.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# Add cache-busting headers for better browser compatibility (especially Chromium)
@app.after_request
def after_request(response):
    # Prevent caching for API endpoints and real-time data
    if request.endpoint and any(x in request.endpoint for x in ['api', 'events', 'statistics']):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Add CORS headers for WebSocket compatibility
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(
    app, 
    async_mode='threading', 
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1000000,
    allow_upgrades=True,
    always_connect=True
)

# Helper function for blockchain logging
def add_to_blockchain(event_type, user_id, details):
    """
    Helper function to add events to blockchain audit trail.
    Uses add_blockchain_event from blockchain_helper module.
    """
    try:
        from blockchain_helper import add_blockchain_event
        blockchain_block = add_blockchain_event(
            event_type=event_type,
            user_id=user_id,
            event_details=details
        )
        print(f"[BLOCKCHAIN] ✅ Event logged: {event_type} - Block #{blockchain_block.block_index}")
        return blockchain_block
    except Exception as e:
        print(f"[BLOCKCHAIN WARNING] Failed to log event: {e}")
        return None

# WebSocket event handlers with enhanced connection tracking
@socketio.on('connect', namespace='/events')
def handle_connect():
    """Handle client connection to WebSocket with detailed logging"""
    client_id = request.sid
    client_info = {
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'remote_addr': request.environ.get('REMOTE_ADDR'),
        'origin': request.headers.get('Origin', 'Unknown')
    }
    
    print(f"[WEBSOCKET] 🔌 CLIENT CONNECTING:")
    print(f"  ├─ Session ID: {client_id}")
    print(f"  ├─ Remote IP: {client_info['remote_addr']}")
    print(f"  ├─ User Agent: {client_info['user_agent'][:50]}...")
    print(f"  ├─ Origin: {client_info['origin']}")
    print(f"  └─ Namespace: /events")
    
    try:
        # Get total connected clients
        rooms = socketio.server.manager.rooms.get('/events', {})
        total_clients = len(rooms)
        
        print(f"[WEBSOCKET] ✅ CONNECTION SUCCESSFUL:")
        print(f"  ├─ Handshake Complete: YES")
        print(f"  ├─ Session Established: {client_id}")
        print(f"  ├─ Total Connected Clients: {total_clients}")
        print(f"  └─ Connection Time: {datetime.now().isoformat()}")
        
        # Send connection confirmation with detailed info
        emit('connection_status', {
            'status': 'connected',
            'message': 'WebSocket handshake successful - Real-time monitoring active',
            'server_time': datetime.now().isoformat(),
            'session_id': client_id,
            'total_clients': total_clients,
            'connection_established': True
        })
        
        # Send immediate ping to test bidirectional communication
        print(f"[WEBSOCKET] 🏓 Sending initial ping to {client_id}")
        emit('server_ping', {
            'timestamp': datetime.now().isoformat(),
            'message': 'Connection test from server'
        })
        
    except Exception as e:
        print(f"[WEBSOCKET ERROR] ❌ CONNECTION HANDLER FAILED: {e}")
        import traceback
        traceback.print_exc()

@socketio.on('disconnect', namespace='/events')
def handle_disconnect(*args):
    """Handle client disconnection from WebSocket
    
    Note: *args is used to accept optional arguments that may be passed
    by different versions of Flask-SocketIO, but we don't use them.
    """
    client_id = request.sid
    try:
        rooms = socketio.server.manager.rooms.get('/events', {})
        remaining_clients = len(rooms) - 1  # Subtract the disconnecting client
        
        print(f"[WEBSOCKET] 🔌 CLIENT DISCONNECTING:")
        print(f"  ├─ Session ID: {client_id}")
        print(f"  ├─ Remaining Clients: {remaining_clients}")
        print(f"  └─ Disconnect Time: {datetime.now().isoformat()}")
        
    except Exception as e:
        print(f"[WEBSOCKET ERROR] ❌ DISCONNECT HANDLER FAILED: {e}")

@socketio.on_error(namespace='/events')
def handle_error(e):
    """Handle WebSocket errors"""
    print(f"[WEBSOCKET ERROR] ❌ ERROR IN /events NAMESPACE: {e}")
    try:
        print(f"  ├─ Session ID: {request.sid}")
        print(f"  ├─ Error Type: {type(e).__name__}")
        print(f"  └─ Error Message: {str(e)}")
    except:
        pass

@socketio.on_error_default
def default_error_handler(e):
    """Handle all other WebSocket errors"""
    print(f"[WEBSOCKET ERROR] ❌ DEFAULT ERROR HANDLER: {e}")
    print(f"  └─ Error Type: {type(e).__name__}")

@socketio.on('ping', namespace='/events')
def handle_ping(data):
    """Handle ping from client for connection testing"""
    client_id = request.sid
    print(f"[WEBSOCKET] 🏓 PING RECEIVED:")
    print(f"  ├─ From Client: {client_id}")
    print(f"  ├─ Data: {data}")
    print(f"  └─ Sending Pong Response...")
    
    emit('pong', {
        'timestamp': datetime.now().isoformat(),
        'client_id': client_id,
        'server_response': 'Connection active'
    })

@socketio.on('client_ready', namespace='/events')
def handle_client_ready(data):
    """Handle client ready signal for connection verification"""
    client_id = request.sid
    print(f"[WEBSOCKET] 📱 CLIENT READY SIGNAL:")
    print(f"  ├─ From Client: {client_id}")
    print(f"  ├─ Client Data: {data}")
    print(f"  └─ Acknowledging client ready state")
    
    emit('server_ack', {
        'status': 'acknowledged',
        'timestamp': datetime.now().isoformat(),
        'message': 'Server received client ready signal'
    })

# Enhanced broadcast function for events
def broadcast_event(event_data, namespace='/events'):
    """Enhanced broadcast function with better error handling"""
    try:
        event_type = event_data.get('event', {}).get('event_type', 'unknown')
        print(f"[WEBSOCKET] 📡 BROADCASTING EVENT:")
        print(f"  ├─ Event Type: {event_type}")
        print(f"  ├─ Event Name: 'new_event'")
        print(f"  ├─ Namespace: {namespace}")
        print(f"  ├─ Connected Clients: {len(socketio.server.manager.rooms.get(namespace, {}))}")
        print(f"  └─ Payload Keys: {list(event_data.keys())}")
        
        # Emit the event
        socketio.emit('new_event', event_data, namespace=namespace)
        
        print(f"[WEBSOCKET] ✅ EVENT BROADCAST SUCCESSFUL - Event '{event_type}' sent to all clients")
    except Exception as e:
        print(f"[WEBSOCKET ERROR] ❌ BROADCAST FAILED: {e}")
        print(f"[WEBSOCKET ERROR] Event data: {event_data}")
        import traceback
        traceback.print_exc()

# GPIO setup - only if not in testing mode
print("[DEBUG] 🔧 Starting GPIO setup...")
if not os.environ.get('TESTING'):
    print("[DEBUG] 🔧 Not in testing mode, initializing GPIO hardware...")
    GPIO.setwarnings(False)
    
    # Kill any lingering GPIO processes before we start
    try:
        print("[DEBUG] 🔧 Checking for lingering GPIO processes...")
        import subprocess
        result = subprocess.run(['lsof', '/dev/gpiomem'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("[DEBUG] 🔧 Found processes using GPIO, attempting cleanup...")
            # Get PIDs using GPIO (excluding current process)
            current_pid = os.getpid()
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1])
                            if pid != current_pid:
                                print(f"[DEBUG] 🔧 Terminating GPIO process PID: {pid}")
                                os.kill(pid, 15)  # SIGTERM
                        except (ValueError, ProcessLookupError, PermissionError):
                            pass
            time.sleep(0.5)  # Give processes time to cleanup
    except FileNotFoundError:
        # lsof not available, skip this cleanup step
        print("[DEBUG] 🔧 lsof not available, skipping process cleanup")
    except Exception as process_cleanup_error:
        print(f"[DEBUG] 🔧 Process cleanup warning: {process_cleanup_error}")
    
    # Enhanced GPIO cleanup and initialization
    try:
        # Aggressive GPIO cleanup for stubborn processes
        print("[DEBUG] 🔧 Performing aggressive GPIO cleanup...")
        
        # Multiple cleanup attempts with different approaches
        for attempt in range(3):
            try:
                GPIO.cleanup()
                print(f"[DEBUG] 🔧 GPIO cleanup attempt {attempt + 1} completed")
                time.sleep(0.2)  # Give time for cleanup
            except Exception as e:
                print(f"[DEBUG] 🔧 Cleanup attempt {attempt + 1} warning: {e}")
        
        # Force reset GPIO mode to ensure clean state
        try:
            # Reset any existing GPIO mode
            GPIO.setmode(GPIO.BOARD)
            print("[DEBUG] 🔧 GPIO mode reset to BOARD")
        except Exception as mode_error:
            print(f"[DEBUG] 🔧 GPIO mode reset warning: {mode_error}")
            try:
                # If BOARD mode fails, try cleanup and set again
                GPIO.cleanup()
                time.sleep(0.3)
                GPIO.setmode(GPIO.BOARD)
                print("[DEBUG] 🔧 GPIO mode set after cleanup")
            except Exception as retry_error:
                print(f"[DEBUG] 🔧 GPIO mode retry warning: {retry_error}")
        
        print("[DEBUG] 🔧 GPIO cleanup and mode initialization completed")
        
        # Setup pins with enhanced error handling and retry logic
        pins_to_setup = [
            (11, GPIO.IN, GPIO.PUD_UP, "Magnetic sensor"),
            (22, GPIO.OUT, None, "Green LED"),
            (13, GPIO.OUT, None, "Red LED"), 
            (16, GPIO.OUT, None, "White LED"),
            (18, GPIO.IN, GPIO.PUD_UP, "Switch")
        ]
        
        successful_pins = []
        failed_pins = []
        
        for pin, mode, pull, description in pins_to_setup:
            success = False
            # Retry each pin up to 3 times with increasing delays
            for retry in range(3):
                try:
                    # Force cleanup this specific pin if needed
                    if retry > 0:
                        try:
                            GPIO.cleanup(pin)
                            time.sleep(0.1 * (retry + 1))  # Increasing delay
                            print(f"[DEBUG] 🔧 Pin {pin} cleanup attempt {retry}")
                        except:
                            pass
                    
                    # Setup the pin
                    if mode == GPIO.IN:
                        GPIO.setup(pin, mode, pull_up_down=pull)
                    else:
                        GPIO.setup(pin, mode)
                    
                    print(f"[DEBUG] ✅ GPIO pin {pin} setup successful ({description})")
                    successful_pins.append((pin, description))
                    success = True
                    break
                    
                except Exception as pin_error:
                    error_msg = str(pin_error).lower()
                    if "gpio busy" in error_msg or "not allocated" in error_msg:
                        print(f"[DEBUG] 🔧 Pin {pin} retry {retry + 1}: {pin_error}")
                        if retry == 2:  # Last retry
                            print(f"[ERROR] ❌ Failed to setup GPIO pin {pin} ({description}) after 3 attempts: {pin_error}")
                            failed_pins.append((pin, description, str(pin_error)))
                    else:
                        print(f"[ERROR] ❌ Failed to setup GPIO pin {pin} ({description}): {pin_error}")
                        failed_pins.append((pin, description, str(pin_error)))
                        break
            
        # Summary report
        print(f"[DEBUG] 🔧 GPIO Setup Summary:")
        print(f"  ├─ Successful pins: {len(successful_pins)}/{len(pins_to_setup)}")
        for pin, desc in successful_pins:
            print(f"  │   ✅ Pin {pin}: {desc}")
        if failed_pins:
            print(f"  └─ Failed pins: {len(failed_pins)}")
            for pin, desc, error in failed_pins:
                print(f"      ❌ Pin {pin}: {desc} ({error})")
                
        print("[DEBUG] 🔧 GPIO initialization completed")
        
    except Exception as e:
        print(f"[ERROR] ❌ GPIO initialization failed: {e}")
        print("[DEBUG] 🔧 Continuing without GPIO (hardware features disabled)")
        # Set testing mode to disable hardware features
        os.environ['TESTING'] = '1'
else:
    print("[DEBUG] 🔧 TESTING mode detected - skipping GPIO hardware initialization")

print("[DEBUG] 🔧 GPIO setup phase completed, continuing with global variables...")

# GPIO availability flag - set to True only if GPIO hardware is properly initialized
gpio_available = False
if not os.environ.get('TESTING'):
    # Check if at least the essential pins are working (pin 11 - door sensor)
    try:
        GPIO.input(11)  # Test if we can read the door sensor
        gpio_available = True
        print("[DEBUG] ✅ GPIO hardware is available and functional")
    except Exception as gpio_test_error:
        print(f"[WARNING] ⚠️ GPIO hardware not available: {gpio_test_error}")
        print("[DEBUG] 🔧 Application will run in SOFTWARE-ONLY mode (no hardware control)")
        gpio_available = False
else:
    print("[DEBUG] 🔧 TESTING mode - GPIO disabled")
    gpio_available = False

# Global variables for door state
door_open = False
alarm_active = False
timer_thread = None
timer_active = False
timer_duration = 30  # Default 30 seconds
alarm_volume = 1.0  # Default alarm volume (0.0 to 1.0) - MAXIMUM VOLUME

# Hardware pin assignments
# Door sensor is connected to GPIO pin 11 (BOARD numbering used in setup)
DOOR_SENSOR_PIN = 11

# Thread management for graceful shutdown
shutdown_flag = threading.Event()
monitor_thread = None

# Audio system health
audio_system_ready = False

# Duplicate prevention variables
last_logged_door_state = None
last_logged_alarm_state = False
last_event_timestamps = {}
event_lock = threading.Lock()
event_counter = 0  # Global counter to track all log_event calls
last_door_event_time = 0  # Track last door event time for minimum interval

# Signal handling and cleanup functions
def cleanup_and_exit():
    """Clean up resources before exit"""
    global shutdown_flag, monitor_thread, timer_thread
    
    print("[DEBUG] 🔧 Cleaning up GPIO before exit...")
    
    # Signal all threads to shutdown
    shutdown_flag.set()
    
    # Wait for monitoring thread to finish
    if monitor_thread and monitor_thread.is_alive():
        print("[DEBUG] 🔧 Waiting for monitor thread to stop...")
        monitor_thread.join(timeout=2.0)
        if monitor_thread.is_alive():
            print("[DEBUG] ⚠️ Monitor thread did not stop within timeout")
    
    # Wait for timer thread to finish
    if timer_thread and timer_thread.is_alive():
        print("[DEBUG] 🔧 Waiting for timer thread to stop...")
        timer_thread.join(timeout=2.0)
        if timer_thread.is_alive():
            print("[DEBUG] ⚠️ Timer thread did not stop within timeout")
    
    # Clean up GPIO
    if not os.environ.get('TESTING'):
        try:
            GPIO.cleanup()
            print("[DEBUG] ✅ GPIO cleanup completed")
        except Exception as e:
            print(f"[DEBUG] ⚠️ GPIO cleanup warning: {e}")

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    print(f"[DEBUG] 🛑 Received signal {signum}, exiting...")
    cleanup_and_exit()
    os._exit(0)

# Register signal handlers and cleanup function
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
atexit.register(cleanup_and_exit)  # Called on normal exit

# Audio initialization function
def initialize_audio():
    """Initialize pygame audio system for alarm sounds"""
    global audio_system_ready, alarm_volume
    
    try:
        print("[DEBUG] 🔊 Initializing audio system...")
        print(f"[DEBUG] Audio file path: {AUDIO_PATH}")
        print(f"[DEBUG] Audio file exists: {AUDIO_PATH.exists()}")
        
        # Enhanced SDL and ALSA configuration for Raspberry Pi
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
        os.environ['ALSA_PCM_DEVICE'] = '0'  # Force headphone jack (card 0)
        
        # Quit any existing mixer to start fresh
        if pygame.mixer.get_init():
            pygame.mixer.quit()
            print("[DEBUG] Existing mixer quit")
            
        # Initialize pygame mixer with optimized settings for Raspberry Pi
        pygame.mixer.pre_init(
            frequency=22050,  # Optimal frequency for Pi
            size=-16,         # 16-bit signed samples
            channels=2,       # Stereo
            buffer=512        # Small buffer for low latency
        )
        pygame.mixer.init()
        
        if not AUDIO_PATH.exists():
            print(f"[WARNING] ⚠️ Audio file missing: {AUDIO_PATH}")
            print("[INFO] Please place your alarm sound file at: static/audio.mp3")
            audio_system_ready = False
            return False
        
        # Check file size
        file_size = AUDIO_PATH.stat().st_size
        print(f"[DEBUG] Audio file size: {file_size} bytes")
        
        # Preload audio for instant playback - load into memory
        global preloaded_sound
        try:
            # Load the sound as a Sound object for instant playback
            preloaded_sound = pygame.mixer.Sound(str(AUDIO_PATH))
            preloaded_sound.set_volume(alarm_volume)
            print(f"[DEBUG] ✅ Audio preloaded into memory for instant playback")
        except Exception as e:
            print(f"[DEBUG] ⚠️ Could not preload as Sound object, falling back to music: {e}")
            # Fallback to music loading
            pygame.mixer.music.load(str(AUDIO_PATH))
            pygame.mixer.music.set_volume(alarm_volume)
        
        print(f"[DEBUG] ✅ Audio initialization successful:")
        print(f"  ├─ File: {AUDIO_PATH}")
        print(f"  ├─ Size: {file_size} bytes")
        print(f"  ├─ Volume: {alarm_volume}")
        print(f"  ├─ Mixer initialized: {pygame.mixer.get_init()}")
        print(f"  ├─ Preloaded: {preloaded_sound is not None}")
        print(f"  └─ SDL Audio Driver: {os.environ.get('SDL_AUDIODRIVER', 'default')}")
        
        audio_system_ready = True
        return True
        
    except Exception as e:
        print(f"[ERROR] ❌ Audio initialization failed: {e}")
        print(f"[ERROR] Exception details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        audio_system_ready = False
        return False

def monitor_alarm_audio():
    """Monitor alarm state and stop audio when alarm is deactivated (audio already playing)"""
    global alarm_active
    
    # Audio is already playing - just monitor the alarm state
    while alarm_active:
        time.sleep(0.1)  # Check alarm status every 100ms
        if not alarm_active:
            print("[DEBUG] 🔇 Alarm deactivated - stopping continuous loop")
            break
    
    print("[DEBUG] 🔇 Audio monitoring stopped")

def play_alarm():
    """Play alarm sound continuously until alarm is deactivated"""
    global alarm_active, audio_system_ready, preloaded_sound
    
    print(f"[DEBUG] 🔊 play_alarm() called:")
    print(f"  ├─ audio_system_ready: {audio_system_ready}")
    print(f"  ├─ alarm_active: {alarm_active}")
    print(f"  ├─ preloaded_sound available: {preloaded_sound is not None}")
    print(f"  └─ pygame mixer initialized: {pygame.mixer.get_init()}")
    
    if not audio_system_ready:
        print("[DEBUG] 🔇 Audio system not ready - skipping alarm sound")
        print("[DEBUG] 🔧 Attempting to reinitialize audio...")
        if initialize_audio():
            print("[DEBUG] ✅ Audio reinitialized successfully")
        else:
            print("[DEBUG] ❌ Audio reinitialization failed")
            return
        
    print(f"[DEBUG] 🔊 Starting audio alarm, volume={alarm_volume}")
    
    try:
        if preloaded_sound:
            # Use preloaded sound for instant playback with looping
            print("[DEBUG] 🎵 Playing preloaded alarm sound in continuous loop...")
            preloaded_sound.set_volume(alarm_volume)
            preloaded_sound.play(loops=-1)  # -1 = infinite loop, no gaps!
            print("[DEBUG] 🔄 Preloaded audio now looping continuously until stopped")
        else:
            # Fallback to music loading if preloaded sound not available
            print("[DEBUG] 🎵 Loading and playing alarm sound...")
            pygame.mixer.music.load(AUDIO_PATH)
            pygame.mixer.music.set_volume(alarm_volume)
            pygame.mixer.music.play(loops=-1)
            print("[DEBUG] 🔄 Audio now looping continuously until stopped")
        
        # Keep the thread alive while alarm is active, checking every 100ms
        while alarm_active:
            time.sleep(0.1)  # Check alarm status every 100ms
            if not alarm_active:
                print("[DEBUG] � Alarm deactivated - stopping continuous loop")
                break
                
        print("[DEBUG] 🔇 Audio alarm stopped")
        
    except Exception as e:
        print(f"[ERROR] ❌ Audio alarm error: {e}")
        import traceback
        traceback.print_exc()
        
def stop_alarm_audio():
    """Stop the alarm audio immediately"""
    global preloaded_sound
    try:
        # Stop both music and sound channels
        pygame.mixer.music.stop()
        pygame.mixer.stop()  # Stop all Sound channels
        print("[DEBUG] 🔇 Audio alarm stopped immediately (both music and sound channels)")
    except Exception as e:
        print(f"[ERROR] ❌ Error stopping audio: {e}")

# Helper function for safe GPIO control
def safe_gpio_output(pin, state, description=""):
    """Safely control GPIO output with error handling"""
    if gpio_available:
        try:
            GPIO.output(pin, state)
            state_str = "HIGH" if state == GPIO.HIGH else "LOW"
            print(f"[DEBUG] 🔧 GPIO Pin {pin} set to {state_str} {description}")
            return True
        except Exception as e:
            print(f"[WARNING] ⚠️ GPIO Pin {pin} control failed {description}: {e}")
            return False
    else:
        state_str = "HIGH" if state else "LOW"
        print(f"[DEBUG] 🔧 GPIO not available - would set Pin {pin} to {state_str} {description}")
        return False

def activate_alarm_led_and_audio():
    """Turn ON white LED and immediately play audio - linked together"""
    global alarm_active, preloaded_sound, alarm_volume
    
    # Turn on white LED first
    if gpio_available:
        try:
            GPIO.output(16, GPIO.HIGH)  # Turn on white LED (alarm)
            print("[DEBUG] 🔴 WHITE LED ON (Pin 16) - ALARM ACTIVE")
            # Verify the LED state immediately after setting it
            actual_state = GPIO.input(16)
            print(f"[DEBUG] 🔍 WHITE LED VERIFICATION: Pin 16 actual state = {actual_state} (should be 1)")
        except Exception as gpio_error:
            print(f"[DEBUG] ⚠️ GPIO error during white LED activation: {gpio_error}")
    else:
        print("[DEBUG] 🔴 GPIO not available - would turn ON white LED")
    
    # Immediately start audio (no conditional checks - always play when LED is on)
    print("[DEBUG] 🎵 AUDIO LINKED TO WHITE LED - Starting alarm sound...")
    
    try:
        if preloaded_sound:
            # Use preloaded sound for instant playback
            preloaded_sound.set_volume(alarm_volume)
            preloaded_sound.play(loops=-1)  # Start immediately in infinite loop
            print("[DEBUG] 🔄 Preloaded audio now playing in continuous loop")
        else:
            # Fallback: try to initialize and play
            if initialize_audio() and preloaded_sound:
                preloaded_sound.set_volume(alarm_volume)
                preloaded_sound.play(loops=-1)
                print("[DEBUG] 🔄 Audio initialized and playing")
            else:
                # Last resort: use pygame music
                if AUDIO_PATH.exists():
                    pygame.mixer.music.load(str(AUDIO_PATH))
                    pygame.mixer.music.set_volume(alarm_volume)
                    pygame.mixer.music.play(loops=-1)
                    print("[DEBUG] 🔄 Fallback music playing")
                else:
                    print("[DEBUG] ❌ No audio file available")
    except Exception as audio_error:
        print(f"[DEBUG] ⚠️ Audio error during alarm activation: {audio_error}")
    
    # Start monitoring thread for alarm state
    threading.Thread(target=monitor_alarm_audio, daemon=True, name="AlarmAudioMonitor").start()

def deactivate_alarm_led_and_audio():
    """Turn OFF white LED and stop audio - linked together"""
    
    # Stop audio first
    stop_alarm_audio()
    
    # Turn off white LED
    if gpio_available:
        try:
            GPIO.output(16, GPIO.LOW)  # Turn off white LED
            print("[DEBUG] ⚫ WHITE LED OFF (Pin 16) - ALARM DEACTIVATED")
        except Exception as gpio_error:
            print(f"[DEBUG] ⚠️ GPIO error during white LED deactivation: {gpio_error}")
    else:
        print("[DEBUG] ⚫ TESTING mode - would turn OFF white LED")

print("[DEBUG] 🔧 Global variables initialized:")
print(f"  ├─ door_open: {door_open}")
print(f"  ├─ alarm_active: {alarm_active}")
print(f"  ├─ timer_active: {timer_active}")
print(f"  └─ timer_duration: {timer_duration}s")

def calculate_uptime():
    """Calculate system uptime since server start"""
    uptime_delta = datetime.now() - SERVER_START_TIME
    
    # Calculate components
    total_seconds = int(uptime_delta.total_seconds())
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    # Format uptime string
    if days > 0:
        uptime_str = f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        uptime_str = f"{hours}h {minutes}m {seconds}s"
    else:
        uptime_str = f"{minutes}m {seconds}s"
    
    # Calculate uptime percentage (assuming 99.9% target)
    total_minutes = uptime_delta.total_seconds() / 60
    if total_minutes > 0:
        # Simple availability calculation (can be enhanced with downtime tracking)
        availability = min(99.99, 99.5 + (total_minutes / 1440) * 0.49)  # Approaches 99.99% over time
    else:
        availability = 100.0
    
    return {
        'uptime_string': uptime_str,
        'uptime_seconds': total_seconds,
        'start_time': SERVER_START_TIME.isoformat(),
        'availability_percent': round(availability, 2),
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds
    }

# Custom Jinja2 filter for formatting dates according to user preferences
@app.template_filter('format_datetime')
def format_datetime_filter(dt, date_format='YYYY-MM-DD', time_format='24h'):
    """
    Format datetime object according to user's preferred date and time format
    Args:
        dt: datetime object
        date_format: User's preferred date format (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD-MM-YYYY)
        time_format: User's preferred time format (24h or 12h)
    """
    if not dt:
        return ''
    
    # Date format mapping
    date_formats = {
        'YYYY-MM-DD': '%Y-%m-%d',
        'DD/MM/YYYY': '%d/%m/%Y',
        'MM/DD/YYYY': '%m/%d/%Y',
        'DD-MM-YYYY': '%d-%m-%Y'
    }
    
    # Time format mapping
    time_formats = {
        '24h': '%H:%M:%S',
        '12h': '%I:%M:%S %p'
    }
    
    # Get the format strings
    date_fmt = date_formats.get(date_format, '%Y-%m-%d')
    time_fmt = time_formats.get(time_format, '%H:%M:%S')
    
    # Combine date and time format
    full_format = f"{date_fmt} {time_fmt}"
    
    return dt.strftime(full_format)

# Initialize system
def init_system():
    os.makedirs('instance', exist_ok=True)
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')  # Change in production!
            db.session.add(admin)
            db.session.commit()
        
        # Set default timer duration if not exists, and load current value
        timer_setting = Setting.query.filter_by(key='timer_duration').first()
        if not timer_setting:
            timer_setting = Setting(key='timer_duration', value='30')
            db.session.add(timer_setting)
            db.session.commit()
        
        # Load timer duration from database
        global timer_duration
        timer_duration = int(timer_setting.value)
        print(f"[DEBUG] ⏰ Timer duration loaded from database: {timer_duration} seconds")
        
        # Initialize LEDs to proper startup state
        if gpio_available:
            try:
                print("[DEBUG] 🔧 Initializing LED states...")
                GPIO.output(22, GPIO.HIGH)  # Green LED on (system ready)
                GPIO.output(13, GPIO.LOW)   # Red LED off (no timer active)
                GPIO.output(16, GPIO.LOW)   # White LED off (no alarm)
                print("[DEBUG] ✅ LEDs initialized - Green: ON, Red: OFF, White: OFF")
            except Exception as led_error:
                print(f"[WARNING] ⚠️ LED initialization failed: {led_error}")
                print("[DEBUG] 🔧 Continuing without LED control...")
        else:
            print("[DEBUG] 🔧 GPIO not available - Skipping LED initialization")
            
        # Initialize audio system
        print("[DEBUG] 🔧 Initializing audio system...")
        initialize_audio()
        
        # Initialize camera system
        print("[DEBUG] 🔧 Initializing camera system...")
        try:
            camera_config = app.config.get('CAMERA_CONFIG', {})
            camera_manager = initialize_camera_manager(camera_config)
            camera_status = camera_manager.get_status()
            
            if camera_status['available']:
                print(f"[DEBUG] ✅ Camera initialized successfully!")
                print(f"[DEBUG]    Type: {camera_status['type']}")
                print(f"[DEBUG]    Resolution: {camera_status['resolution']}")
                print(f"[DEBUG]    Storage: {camera_status['storage_path']}")
            else:
                print("[DEBUG] ℹ️  Camera not detected - Event images disabled")
                print("[DEBUG]    System will work normally without camera")
                print("[DEBUG]    Plug in USB webcam and restart to enable image capture")
        except Exception as camera_error:
            print(f"[WARNING] ⚠️  Camera initialization failed: {camera_error}")
            print("[DEBUG] 🔧 Continuing without camera (non-critical)...")

# ============================================================================
# ANOMALY DETECTION SYSTEM
# ============================================================================

def detect_anomalies(event_type, event_id=None):
    """
    Detect anomalous door access patterns and log them
    
    Anomaly types:
    1. odd_hours - Door accessed outside business hours
    2. repeated_opens - Multiple opens in short timeframe (3+ in 10 minutes)
    3. prolonged_open - Door left open beyond threshold (2x timer duration)
    """
    try:
        with app.app_context():
            # Get business hours setting (default 9-17 for 9am-5pm)
            business_hours_start = 9
            business_hours_end = 17
            
            # Check if there's a setting for business hours
            bh_start_setting = Setting.query.filter_by(key='business_hours_start').first()
            bh_end_setting = Setting.query.filter_by(key='business_hours_end').first()
            
            if bh_start_setting:
                business_hours_start = int(bh_start_setting.value)
            if bh_end_setting:
                business_hours_end = int(bh_end_setting.value)
            
            current_hour = datetime.now().hour
            current_time = datetime.now()
            
            # 1. Odd hours detection
            if event_type == 'door_open':
                if current_hour < business_hours_start or current_hour >= business_hours_end:
                    anomaly = AnomalyDetection(
                        event_id=event_id,
                        anomaly_type='odd_hours',
                        severity='medium',
                        description=f'Door accessed outside business hours ({current_hour}:00 - Business hours: {business_hours_start}:00-{business_hours_end}:00)',
                        detected_at=current_time
                    )
                    db.session.add(anomaly)
                    db.session.commit()
                    
                    print(f"[ANOMALY] 🚨 Odd hours access detected at {current_hour}:00")
                    
                    # Emit WebSocket event for real-time alert
                    socketio.emit('anomaly_detected', {
                        'type': 'odd_hours',
                        'severity': 'medium',
                        'message': f'Door accessed outside business hours',
                        'time': current_time.strftime('%Y-%m-%d %H:%M:%S')
                    }, namespace='/events')
            
            # 2. Repeated opens detection (3+ opens in last 10 minutes)
            if event_type == 'door_open':
                ten_minutes_ago = current_time - timedelta(minutes=10)
                recent_opens = EventLog.query.filter(
                    EventLog.event_type == 'door_open',
                    EventLog.timestamp >= ten_minutes_ago
                ).count()
                
                if recent_opens >= 3:  # Including current event
                    anomaly = AnomalyDetection(
                        event_id=event_id,
                        anomaly_type='repeated_opens',
                        severity='high',
                        description=f'Repeated door access detected: {recent_opens} opens in last 10 minutes',
                        detected_at=current_time
                    )
                    db.session.add(anomaly)
                    db.session.commit()
                    
                    print(f"[ANOMALY] 🚨 Repeated opens: {recent_opens} times in 10 minutes")
                    
                    socketio.emit('anomaly_detected', {
                        'type': 'repeated_opens',
                        'severity': 'high',
                        'message': f'{recent_opens} door opens in 10 minutes',
                        'time': current_time.strftime('%Y-%m-%d %H:%M:%S')
                    }, namespace='/events')
            
            # 3. Prolonged open detection (handled in alarm_timer when alarm triggers)
            # This will be called from alarm_timer when alarm is triggered
            
    except Exception as e:
        print(f"[ERROR] Anomaly detection failed: {e}")
        import traceback
        traceback.print_exc()

# Door monitoring thread
def monitor_door():
    global door_open, alarm_active, timer_active, timer_duration, timer_thread, shutdown_flag
    last_gpio_state = None
    state_change_time = 0
    
    print("[DEBUG] 🚪 Door monitoring loop started")
    
    # Check if GPIO is available
    if not gpio_available:
        print("[DEBUG] 🚪 GPIO not available - Door monitoring disabled (software-only mode)")
        while not shutdown_flag.is_set():
            time.sleep(1)
        return
    
    while not shutdown_flag.is_set():
        try:
            if os.environ.get('TESTING'):
                time.sleep(1)  # Don't monitor in testing mode
                continue
                
            # Check for shutdown before GPIO operations
            if shutdown_flag.is_set():
                break
                
            # For NO sensor: HIGH means door open, LOW means door closed
            current_gpio_state = GPIO.input(11) == GPIO.HIGH  # NO mode
            
            # Add periodic debug output every 5 seconds
            if int(time.time()) % 5 == 0:
                print(f"[DEBUG] 🔍 Door monitoring: GPIO pin 11 = {GPIO.input(11)}, interpreted as {'OPEN' if current_gpio_state else 'CLOSED'}")
                time.sleep(1)  # Prevent multiple prints in same second
            
            # GPIO debouncing - only process state changes after stable for 50ms
            if current_gpio_state != last_gpio_state:
                print(f"[DEBUG] 🚪 Door state change detected: {last_gpio_state} -> {current_gpio_state}")
                state_change_time = time.time()
                last_gpio_state = current_gpio_state
                continue
                
        except Exception as gpio_error:
            if shutdown_flag.is_set():
                print("[DEBUG] 🚪 Monitor thread shutting down...")
                break
            print(f"[DEBUG] ⚠️ GPIO error in monitor_door: {gpio_error}")
            # If GPIO is not available, wait and retry
            time.sleep(0.5)
            continue
        
        # Check if state has been stable for at least 50ms
        if time.time() - state_change_time < 0.05:
            continue
            
        door_is_open = current_gpio_state

        if door_is_open and not door_open:
            # Door just opened - check minimum time between events
            global last_door_event_time
            current_time = time.time()
            if current_time - last_door_event_time < 1.0:  # Minimum 1 second between door events
                print(f"[DEBUG] Door event too soon after last event, ignoring (time since last: {current_time - last_door_event_time:.3f}s)")
                continue
                
            door_open = True
            alarm_active = False
            timer_active = True
            last_door_event_time = current_time
            
            # Ensure proper LED states when door opens
            safe_gpio_output(16, GPIO.LOW, "(White LED - ensure alarm off)")
            safe_gpio_output(13, GPIO.LOW, "(Red LED - ensure timer LED off before blinking)")
                
            with app.app_context():
                timer_setting = Setting.query.filter_by(key='timer_duration').first()
                if timer_setting:
                    current_timer_duration = int(timer_setting.value)
                    print(f"[DEBUG] ✅ Timer setting found in DB: {current_timer_duration} seconds")
                else:
                    current_timer_duration = 30
                    print(f"[DEBUG] ⚠️  No timer setting in DB, using default: {current_timer_duration} seconds")
            
            # Update global timer_duration for consistency
            timer_duration = current_timer_duration
            
            print(f"[DEBUG] 🚪 DOOR OPENED EVENT:")
            print(f"  ├─ Timer Duration: {current_timer_duration} seconds")
            print(f"  ├─ Global timer_duration: {timer_duration} seconds")
            print(f"  ├─ Current Time: {current_time}")
            print(f"  └─ Will trigger alarm at: {current_time + current_timer_duration}")
            log_event('door_open', 'Door opened')
            
            # Improved timer thread management with proper cleanup
            if timer_thread and timer_thread.is_alive():
                print("[DEBUG] Stopping existing timer thread...")
                timer_active = False  # Signal old thread to stop
                timer_thread.join(timeout=2.0)  # Wait max 2 seconds for cleanup
                if timer_thread.is_alive():
                    print("[WARNING] Previous timer thread did not stop cleanly")
                    
            # Start new timer thread
            timer_active = True  # Reset timer flag before starting new thread
            timer_thread = threading.Thread(target=alarm_timer, args=(current_timer_duration,))
            timer_thread.daemon = True  # Ensure thread dies with main program
            timer_thread.start()
            print(f"[DEBUG] ⏰ New timer thread started for {current_timer_duration}s")
            print(f"[DEBUG] 🔍 Verification - Thread args: {timer_thread._args}")
            
        elif not door_is_open and door_open:
            # Door just closed - check minimum time between events
            current_time = time.time()
            if current_time - last_door_event_time < 1.0:  # Minimum 1 second between door events
                print(f"[DEBUG] Door event too soon after last event, ignoring (time since last: {current_time - last_door_event_time:.3f}s)")
                continue
                
            # Door closed - immediately stop all timers and alarms
            print(f"[DEBUG] 🚪 Door closed - stopping all timers and alarms")
            door_open = False
            alarm_active = False
            timer_active = False  # This signals the timer thread to stop immediately
            last_door_event_time = current_time
            
            # Turn off red LED and deactivate alarm (white LED + audio linked)
            safe_gpio_output(13, GPIO.LOW, "(Red LED - door closed)")
            
            # Deactivate alarm: white LED OFF + audio stop (linked together)
            deactivate_alarm_led_and_audio()
            
            print("[DEBUG] ✅ Door closed. Timer and alarm deactivated.")
            log_event('door_close', 'Door closed')
        time.sleep(0.1)
        
    print("[DEBUG] 🚪 Door monitoring thread exiting...")

def alarm_timer(duration):
    global timer_active, alarm_active, door_open, shutdown_flag
    start_time = time.time()
    print(f"[DEBUG] ⏰ ALARM TIMER STARTED:")
    print(f"  ├─ Duration: {duration} seconds")
    print(f"  ├─ Start Time: {start_time}")
    print(f"  ├─ Timer Active: {timer_active}")
    print(f"  └─ Door Open: {door_open}")
    print(f"  🎯 EXPECTED TRIGGER TIME: {start_time + duration} ({duration}s from now)")
    
    # Simple approach: toggle LED every 0.5 seconds for precise 1-second cycles
    last_toggle_time = start_time
    led_state = False  # Start with LED OFF
    blinks_completed = 0
    
    # Ensure red LED starts OFF when timer begins
    safe_gpio_output(13, GPIO.LOW, "(Red LED - timer start)")
    
    print(f"[DEBUG] 🔴 LED will blink {duration} times (1 blink = 1 second)")
    print(f"[DEBUG] 🎯 Timer will expire at: {start_time + duration:.3f}")
    
    # Blink red LED - toggle every 0.5 seconds for 1-second cycles
    last_debug_second = -1  # Track last debug output second
    while timer_active and (time.time() - start_time) < duration and not shutdown_flag.is_set():
        current_time = time.time()
        elapsed_time = current_time - start_time
        remaining_time = duration - elapsed_time
        
        # Every 1 second, show detailed timing information
        current_second = int(elapsed_time)
        if current_second != last_debug_second and current_second < duration:
            print(f"[DEBUG] ⏱️  Second {current_second + 1}: Elapsed={elapsed_time:.1f}s, Remaining={remaining_time:.1f}s")
            last_debug_second = current_second
        
        # Exit immediately if door closed, timer deactivated, or shutdown requested
        if not timer_active or not door_open or shutdown_flag.is_set():
            print(f"[DEBUG] ❌ Timer interrupted - timer_active: {timer_active}, door_open: {door_open}, shutdown: {shutdown_flag.is_set()}")
            break
        
        # Check if 0.5 seconds have passed since last toggle
        if current_time - last_toggle_time >= 0.5:
            # Toggle LED state
            led_state = not led_state
            last_toggle_time = current_time
            
            safe_gpio_output(13, GPIO.HIGH if led_state else GPIO.LOW, "(Red LED - timer blink)")
            
            if led_state:
                # LED turned ON - start of new blink
                blinks_completed += 1
                print(f"[DEBUG] 🔴 RED LED ON - Blink #{blinks_completed} - Elapsed: {elapsed_time:.1f}s - Remaining: {remaining_time:.1f}s")
            else:
                # LED turned OFF - end of blink
                print(f"[DEBUG] ⚫ RED LED OFF - Blink #{blinks_completed} complete - Elapsed: {elapsed_time:.1f}s")
        
        # Short sleep to prevent excessive CPU usage
        time.sleep(0.1)  # Check every 100ms - less frequent but still responsive
    
    # Timer completed or interrupted - handle final state
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"[DEBUG] 🏁 TIMER LOOP ENDED:")
    print(f"  ├─ Start Time: {start_time:.3f}")
    print(f"  ├─ End Time: {end_time:.3f}")
    print(f"  ├─ Elapsed Time: {elapsed_time:.3f} seconds")
    print(f"  ├─ Expected Duration: {duration} seconds")
    print(f"  ├─ Timer Active: {timer_active}")
    print(f"  ├─ Door Open: {door_open}")
    print(f"  └─ Should Trigger: {timer_active and door_open and elapsed_time >= duration}")
    
    # Ensure red LED is OFF before proceeding
    safe_gpio_output(13, GPIO.LOW, "(Red LED - timer cleanup)")
    print("[DEBUG] 🔴 Red LED turned OFF")
    
    # Check if we should trigger alarm (timer fully elapsed with door still open)
    if timer_active and door_open and elapsed_time >= duration:
        # Timer elapsed and door is still open - trigger alarm
        timer_active = False
        alarm_active = True
        print(f"[DEBUG] ⚠️ ALARM TRIGGERED:")
        print(f"  ├─ Duration Set: {duration} seconds")
        print(f"  ├─ Actual Elapsed: {elapsed_time:.2f} seconds")
        print(f"  ├─ Door Still Open: {door_open}")
        print(f"  └─ Timer Was Active: {timer_active}")
        
        # Ensure red LED is OFF before alarm
        safe_gpio_output(13, GPIO.LOW, "(Red LED - before alarm activation)")
        
        # Activate alarm: white LED ON + audio playing (linked together)
        activate_alarm_led_and_audio()
        
        log_event('alarm_triggered', f'Alarm triggered after {duration} seconds')
        
        # Detect prolonged open anomaly
        with app.app_context():
            try:
                # Get the alarm event that was just logged
                alarm_event = EventLog.query.filter_by(event_type='alarm_triggered').order_by(EventLog.timestamp.desc()).first()
                if alarm_event:
                    anomaly = AnomalyDetection(
                        event_id=alarm_event.id,
                        anomaly_type='prolonged_open',
                        severity='high',
                        description=f'Door left open for {duration} seconds (exceeded threshold)',
                        detected_at=datetime.now()
                    )
                    db.session.add(anomaly)
                    db.session.commit()
                    
                    print(f"[ANOMALY] 🚨 Prolonged open detected: {duration}s")
                    
                    socketio.emit('anomaly_detected', {
                        'type': 'prolonged_open',
                        'severity': 'high',
                        'message': f'Door open for {duration} seconds',
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }, namespace='/events')
            except Exception as e:
                print(f"[ERROR] Failed to log prolonged_open anomaly: {e}")
        
        send_alarm_email(duration)
        
    else:
        # Timer was cancelled or door closed before timer elapsed
        timer_active = False
        # Only set alarm_active to False if door is actually closed
        if not door_open:
            alarm_active = False
        
        # Handle LED states
        safe_gpio_output(13, GPIO.LOW, "(Red LED - timer cancelled)")
        
        # Only deactivate alarm (white LED + audio) if door is actually closed
        if not door_open:
            deactivate_alarm_led_and_audio()
            print(f"[DEBUG] 💡 Alarm fully deactivated - door is closed")
        else:
            print(f"[DEBUG] 💡 Alarm kept active - door still open")
        
        if door_open:
            print(f"[DEBUG] ⏹️ Alarm timer cancelled after {elapsed_time:.2f}s (timer was deactivated)")
        else:
            print(f"[DEBUG] ✅ Alarm timer completed normally - door closed after {elapsed_time:.2f}s")
    
    print(f"[DEBUG] Timer thread ending - Final state: timer_active={timer_active}, alarm_active={alarm_active}")

def log_event(event_type, description):
    from pytz import timezone
    import uuid
    global door_open, alarm_active, last_logged_door_state, last_logged_alarm_state, last_event_timestamps, event_counter
    
    # Generate unique event ID for tracking
    event_id = str(uuid.uuid4())[:8]
    
    # Simplified duplicate prevention with single check method
    with event_lock:
        event_counter += 1
        call_id = event_counter
        current_time = time.time()
        # Use only event_type for duplicate prevention (not description which may be dynamic)
        event_key = event_type
        
        print(f"[DEBUG] log_event #{call_id} [{event_id}]: {event_type} - {description}")
        
        # Single time-based duplicate prevention (simpler and more reliable)
        if event_key in last_event_timestamps:
            time_diff = current_time - last_event_timestamps[event_key]
            if time_diff < 2.0:  # Prevent duplicates within 2 seconds
                print(f"[DEBUG] *** DUPLICATE PREVENTED [{event_id}] ***: {event_type} (time_diff: {time_diff:.3f}s)")
                return
        
        # Update timestamp immediately to prevent race conditions
        last_event_timestamps[event_key] = current_time
        print(f"[DEBUG] *** EVENT APPROVED FOR LOGGING [{event_id}] ***: {event_type}")
        
        # State tracking for consistency (but don't block based on this)
        if event_type == 'door_open':
            last_logged_door_state = True
        elif event_type == 'door_close':
            last_logged_door_state = False
        elif event_type == 'alarm_triggered':
            last_logged_alarm_state = True
        
        # DATABASE INSERTION - single transaction
        try:
            with app.app_context():
                print(f"[DEBUG] Starting DB transaction [{event_id}]...")
                
                # Convert timestamp to IST
                ist = timezone('Asia/Kolkata')
                now_ist = datetime.now(ist)
                event = EventLog(event_type=event_type, description=description, timestamp=now_ist)
                db.session.add(event)
                db.session.commit()
                
                print(f"[DEBUG] ✅ DB COMMIT SUCCESS [{event_id}]: {event_type} -> DB")
                
                # CAMERA CAPTURE - Capture image for door events
                try:
                    camera_config = app.config.get('CAMERA_CONFIG', {})
                    should_capture = (
                        (event_type == 'door_open' and camera_config.get('capture_on_open', True)) or
                        (event_type == 'door_close' and camera_config.get('capture_on_close', True)) or
                        (event_type == 'alarm_triggered' and camera_config.get('capture_on_alarm', True))
                    )
                    
                    if should_capture:
                        print(f"[DEBUG] 📸 Attempting to capture image for {event_type}...")
                        capture_result = capture_event_image(event_type=event_type, event_id=event.id)
                        
                        if capture_result and capture_result.get('success'):
                            # Update event record with image info
                            event.image_path = capture_result['path']
                            event.image_hash = capture_result['hash']
                            event.image_timestamp = capture_result['timestamp']
                            db.session.commit()
                            
                            print(f"[DEBUG] ✅ IMAGE CAPTURED [{event_id}]:")
                            print(f"[DEBUG]    File: {capture_result['filename']}")
                            print(f"[DEBUG]    Size: {capture_result['size_bytes']} bytes")
                            print(f"[DEBUG]    Hash: {capture_result['hash'][:16]}...")
                        else:
                            print(f"[DEBUG] ℹ️  No image captured (camera not available)")
                except Exception as camera_error:
                    # Don't fail event logging if camera fails
                    print(f"[WARNING] Camera capture failed [{event_id}]: {camera_error}")
                
                # BLOCKCHAIN LOGGING - Add to immutable blockchain audit trail
                try:
                    from blockchain_helper import add_blockchain_event
                    user_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None
                    blockchain_block = add_blockchain_event(
                        event_type=event_type,
                        description=description,
                        user_id=user_id,
                        ip_address=request.remote_addr if request else None
                    )
                    print(f"[DEBUG] ✅ BLOCKCHAIN COMMIT SUCCESS [{event_id}]: Block #{blockchain_block.block_index}")
                except Exception as blockchain_error:
                    # Don't fail the entire event if blockchain fails
                    print(f"[WARNING] Blockchain logging failed [{event_id}]: {blockchain_error}")
                
                # Run anomaly detection for door events
                if event_type in ['door_open', 'door_close', 'alarm_triggered']:
                    detect_anomalies(event_type, event.id)
                
                # Refresh event from database to get updated image fields
                db.session.refresh(event)
                
                # Get updated statistics (in same transaction)
                total_events = EventLog.query.count()
                door_open_events = EventLog.query.filter_by(event_type='door_open').count()
                door_close_events = EventLog.query.filter_by(event_type='door_close').count()
                alarm_events = EventLog.query.filter_by(event_type='alarm_triggered').count()
                
                # Get timer setting
                timer_setting = Setting.query.filter_by(key='timer_duration').first()
                timer_set = timer_setting.value if timer_setting else '30'
                
                # Prepare real-time status payload
                last_event = EventLog.query.order_by(EventLog.timestamp.desc()).first()
                payload = {
                    'event': event.to_dict(),
                    'door_status': 'Open' if door_open else 'Closed',
                    'alarm_status': 'Active' if alarm_active else 'Inactive',
                    'timer_set': timer_set,
                    'last_event': last_event.to_dict() if last_event else None,
                    'statistics': {
                        'total_events': total_events,
                        'door_open_events': door_open_events,
                        'door_close_events': door_close_events,
                        'alarm_events': alarm_events
                    },
                    'event_id': event_id  # Add tracking ID
                }
                
                print(f"[DEBUG] Broadcasting WebSocket [{event_id}]: {event_type}")
                print(f"[DEBUG] Event data being broadcast:")
                print(f"[DEBUG]   - ID: {event.id}")
                print(f"[DEBUG]   - Type: {event.event_type}")
                print(f"[DEBUG]   - Image Path: {event.image_path}")
                print(f"[DEBUG]   - Image Hash: {event.image_hash[:16] if event.image_hash else 'None'}...")
                print(f"[DEBUG]   - Full event dict: {payload['event']}")
                
                # Broadcast event to all connected clients
                broadcast_event(payload)
                print(f"[DEBUG] ✅ EVENT COMPLETE [{event_id}]: {event_type}")
                
        except Exception as e:
            print(f"[ERROR] Database error [{event_id}]: {e}")
            # Rollback on error
            try:
                db.session.rollback()
                print(f"[DEBUG] DB ROLLBACK [{event_id}]")
            except:
                pass

def send_alarm_email(duration):
    try:
        print(f"[DEBUG] Attempting to send alarm email for duration: {duration}s")
        
        with app.app_context():
            email_config = EmailConfig.query.first()
            if not email_config:
                print("[DEBUG] No email configuration found in database")
                return
                
            if not email_config.is_configured:
                print("[DEBUG] Email configuration is not marked as configured")
                return
                
            if not email_config.sender_email or not email_config.app_password or not email_config.recipient_emails:
                print(f"[DEBUG] Email configuration incomplete: sender={bool(email_config.sender_email)}, password={bool(email_config.app_password)}, recipients={bool(email_config.recipient_emails)}")
                return
            
            print(f"[DEBUG] Email config found - Sender: {email_config.sender_email}")
            print(f"[DEBUG] Recipients: {email_config.recipient_emails}")
            
            recipients = [email.strip() for email in email_config.recipient_emails.split(',')]
            
            msg = MIMEMultipart()
            msg['From'] = email_config.sender_email
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = "🚨 DOOR ALARM TRIGGERED - BSM Security System"
            
            body = f"""
🚨 SECURITY ALERT: Door alarm has been triggered!

📅 Date & Time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M:%S %p')}
⏱️  Duration: {duration} seconds
🚪 Location: Main Door Security System
🏢 Facility: BSM Science and Technology Solutions

⚠️  IMMEDIATE ACTION REQUIRED:
Please check the door and premises immediately for security.

This is an automated alert from the BSM Door Alarm System v2.0
System Status: OPERATIONAL
Alert Priority: HIGH

---
BSM Science and Technology Solutions
Advanced Door Security & Monitoring Systems
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            print("[DEBUG] Connecting to Gmail SMTP...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            
            print("[DEBUG] Attempting login...")
            server.login(email_config.sender_email, email_config.app_password)
            
            print(f"[DEBUG] Sending email to {len(recipients)} recipients...")
            text = msg.as_string()
            server.sendmail(email_config.sender_email, recipients, text)
            server.quit()
            
            print(f"[SUCCESS] Alarm email sent successfully to: {', '.join(recipients)}")
            
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication failed - check email credentials: {e}"
        print(f"[ERROR] {error_msg}")
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error occurred: {e}"
        print(f"[ERROR] {error_msg}")
    except Exception as e:
        error_msg = f"Email sending failed with unexpected error: {e}"
        print(f"[ERROR] {error_msg}")

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class AdminSettingsForm(FlaskForm):
    timer_duration = IntegerField('Alarm Timer (seconds)', validators=[DataRequired()])
    sender_email = StringField('Sender Email', validators=[DataRequired(), resilient_email])
    app_password = PasswordField('App Password', validators=[DataRequired()])
    recipient_emails = StringField('Recipient Emails (comma separated)', validators=[DataRequired()])

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField('Admin User')
    permissions = SelectMultipleField('Permissions', 
        choices=[
            ('dashboard', 'Dashboard'),
            ('controls', 'Controls'),
            ('event_log', 'Event Log'),
            ('report', 'Report'),
            ('analytics', 'Analytics'),
            ('admin', 'Admin')
        ],
        validators=[DataRequired()]
    )

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            
            # Check if admin needs onboarding
            if user.is_admin:
                email_config = EmailConfig.query.first()
                if not email_config or not email_config.is_configured:
                    return redirect(url_for('admin_onboarding'))
                    
            return redirect(url_for('dashboard'))
        return render_template('login.html', form=form, error='Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ============================================================================
# TRAINING MANAGEMENT ROUTES - 21 CFR Part 11 Phase 3
# ============================================================================

@app.route('/training')
@login_required
def training_dashboard():
    """Training management dashboard"""
    from models import TrainingModule, TrainingRecord
    
    # Get all training modules
    modules = TrainingModule.query.filter_by(is_active=True).all()
    
    # Get user's training records
    if current_user.is_admin:
        # Admin sees all records
        records = TrainingRecord.query.order_by(TrainingRecord.completed_date.desc()).limit(50).all()
        
        # Training statistics
        total_modules = TrainingModule.query.count()
        active_modules = TrainingModule.query.filter_by(is_active=True).count()
        total_completions = TrainingRecord.query.count()
        expired_trainings = TrainingRecord.query.filter(
            TrainingRecord.expiration_date < datetime.utcnow(),
            TrainingRecord.status == 'completed'
        ).count()
    else:
        # Regular users see only their records
        records = TrainingRecord.query.filter_by(user_id=current_user.id).order_by(
            TrainingRecord.completed_date.desc()
        ).all()
        
        total_modules = len(modules)
        active_modules = total_modules
        total_completions = len([r for r in records if r.status == 'completed'])
        expired_trainings = len([r for r in records if r.is_expired()])
    
    return render_template('training/dashboard.html',
                         modules=modules,
                         records=records,
                         total_modules=total_modules,
                         active_modules=active_modules,
                         total_completions=total_completions,
                         expired_trainings=expired_trainings,
                         title='Training Management')

@app.route('/training/modules')
@login_required
def training_modules():
    """List all training modules"""
    from models import TrainingModule
    
    if current_user.is_admin:
        modules = TrainingModule.query.order_by(TrainingModule.created_at.desc()).all()
    else:
        modules = TrainingModule.query.filter_by(is_active=True).all()
    
    return render_template('training/modules.html',
                         modules=modules,
                         title='Training Modules')

@app.route('/training/module/<int:module_id>')
@login_required
def training_module_detail(module_id):
    """View training module details"""
    from models import TrainingModule, TrainingRecord
    
    module = TrainingModule.query.get_or_404(module_id)
    
    # Get user's completion record if exists
    user_record = TrainingRecord.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).order_by(TrainingRecord.completed_date.desc()).first()
    
    # Get all completion records (admin only)
    if current_user.is_admin:
        all_records = TrainingRecord.query.filter_by(module_id=module_id).all()
        completion_count = len([r for r in all_records if r.status == 'completed'])
    else:
        all_records = None
        completion_count = None
    
    return render_template('training/module_detail.html',
                         module=module,
                         user_record=user_record,
                         all_records=all_records,
                         completion_count=completion_count,
                         title=module.module_name)

@app.route('/training/module/create', methods=['GET', 'POST'])
@login_required
def create_training_module():
    """Create new training module (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('training_dashboard'))
    
    from models import TrainingModule
    
    if request.method == 'POST':
        try:
            module = TrainingModule(
                module_name=request.form.get('module_name'),
                description=request.form.get('description'),
                content=request.form.get('content'),
                required_for_roles=request.form.get('required_for_roles'),
                validity_period_days=int(request.form.get('validity_period_days', 365)),
                version=request.form.get('version', '1.0'),
                created_by=current_user.id,
                is_active=True
            )
            
            db.session.add(module)
            db.session.commit()
            
            flash(f'Training module "{module.module_name}" created successfully!', 'success')
            return redirect(url_for('training_modules'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating training module: {str(e)}', 'danger')
    
    return render_template('training/create_module.html', title='Create Training Module')

@app.route('/training/module/<int:module_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_training_module(module_id):
    """Edit training module (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('training_dashboard'))
    
    from models import TrainingModule
    
    module = TrainingModule.query.get_or_404(module_id)
    
    if request.method == 'POST':
        try:
            module.module_name = request.form.get('module_name')
            module.description = request.form.get('description')
            module.content = request.form.get('content')
            module.required_for_roles = request.form.get('required_for_roles')
            module.validity_period_days = int(request.form.get('validity_period_days', 365))
            module.version = request.form.get('version')
            module.is_active = request.form.get('is_active') == 'on'
            
            db.session.commit()
            
            flash(f'Training module "{module.module_name}" updated successfully!', 'success')
            return redirect(url_for('training_module_detail', module_id=module.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating training module: {str(e)}', 'danger')
    
    return render_template('training/edit_module.html', module=module, title='Edit Training Module')

@app.route('/training/module/<int:module_id>/complete', methods=['GET', 'POST'])
@login_required
def complete_training(module_id):
    """Complete training with electronic signature"""
    from models import TrainingModule, TrainingRecord, ElectronicSignature
    from datetime import timedelta
    import hashlib
    
    module = TrainingModule.query.get_or_404(module_id)
    
    if request.method == 'POST':
        try:
            # Verify password for electronic signature
            password = request.form.get('password')
            if not current_user.check_password(password):
                flash('Invalid password. Electronic signature failed.', 'danger')
                return redirect(url_for('complete_training', module_id=module_id))
            
            reason = request.form.get('reason', 'Training completion attestation')
            score = request.form.get('score')
            
            # Calculate expiration date
            completed_date = datetime.utcnow()
            expiration_date = completed_date + timedelta(days=module.validity_period_days)
            
            # Create electronic signature
            signature_data = f"{current_user.username}:{password}:{completed_date.isoformat()}:training_completion"
            signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
            
            signature = ElectronicSignature(
                user_id=current_user.id,
                event_type='training_completion',
                action=f'Completed training: {module.module_name}',
                reason=reason,
                signature_hash=signature_hash,
                ip_address=request.remote_addr,
                timestamp=completed_date
            )
            db.session.add(signature)
            db.session.flush()  # Get signature ID
            
            # Create training record
            record = TrainingRecord(
                user_id=current_user.id,
                module_id=module_id,
                completed_date=completed_date,
                expiration_date=expiration_date,
                signature_id=signature.id,
                score=int(score) if score else None,
                status='completed'
            )
            db.session.add(record)
            db.session.commit()
            
            flash(f'Training "{module.module_name}" completed successfully with electronic signature!', 'success')
            return redirect(url_for('training_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error completing training: {str(e)}', 'danger')
    
    # Check if already completed
    existing_record = TrainingRecord.query.filter_by(
        user_id=current_user.id,
        module_id=module_id,
        status='completed'
    ).order_by(TrainingRecord.completed_date.desc()).first()
    
    return render_template('training/complete_training.html',
                         module=module,
                         existing_record=existing_record,
                         title=f'Complete Training: {module.module_name}')

@app.route('/training/assign', methods=['GET', 'POST'])
@login_required
def assign_training():
    """Assign training to users (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('training_dashboard'))
    
    from models import TrainingModule, User
    
    modules = TrainingModule.query.filter_by(is_active=True).all()
    users = User.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            module_ids = request.form.getlist('modules')
            user_ids = request.form.getlist('users')
            
            # Note: Assignment tracking can be implemented via notifications or separate model
            # For now, we just show which trainings are required based on roles
            
            flash(f'{len(module_ids)} training modules assigned to {len(user_ids)} users.', 'success')
            return redirect(url_for('training_dashboard'))
            
        except Exception as e:
            flash(f'Error assigning training: {str(e)}', 'danger')
    
    return render_template('training/assign_training.html',
                         modules=modules,
                         users=users,
                         title='Assign Training')

@app.route('/training/reports')
@login_required
def training_reports():
    """Training compliance reports (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('training_dashboard'))
    
    from models import TrainingModule, TrainingRecord, User
    from sqlalchemy import func
    
    # Get all users and their training status
    users = User.query.filter_by(is_active=True).all()
    modules = TrainingModule.query.filter_by(is_active=True).all()
    
    # Build user training matrix
    user_training = []
    for user in users:
        user_data = {
            'user': user,
            'completed': 0,
            'expired': 0,
            'pending': 0,
            'records': []
        }
        
        for module in modules:
            record = TrainingRecord.query.filter_by(
                user_id=user.id,
                module_id=module.id
            ).order_by(TrainingRecord.completed_date.desc()).first()
            
            if record:
                user_data['records'].append({
                    'module': module,
                    'record': record,
                    'status': 'expired' if record.is_expired() else 'completed'
                })
                if record.is_expired():
                    user_data['expired'] += 1
                else:
                    user_data['completed'] += 1
            else:
                user_data['records'].append({
                    'module': module,
                    'record': None,
                    'status': 'pending'
                })
                user_data['pending'] += 1
        
        user_training.append(user_data)
    
    # Overall statistics
    total_completions = TrainingRecord.query.filter_by(status='completed').count()
    expired_count = TrainingRecord.query.filter(
        TrainingRecord.expiration_date < datetime.utcnow(),
        TrainingRecord.status == 'completed'
    ).count()
    
    return render_template('training/reports.html',
                         user_training=user_training,
                         modules=modules,
                         total_completions=total_completions,
                         expired_count=expired_count,
                         title='Training Reports')


# ============================================================================
# CHANGE CONTROL ROUTES (21 CFR Part 11 Compliance)
# ============================================================================

@app.route('/change-control')
@login_required
def change_control_dashboard():
    """Change control dashboard"""
    from models import ChangeControl, User
    
    # Get all change requests
    changes = ChangeControl.query.order_by(ChangeControl.requested_date.desc()).all()
    
    # Get statistics
    total_changes = len(changes)
    pending_changes = len([c for c in changes if c.status == 'pending'])
    approved_changes = len([c for c in changes if c.status == 'approved'])
    implemented_changes = len([c for c in changes if c.status == 'implemented'])
    rejected_changes = len([c for c in changes if c.status == 'rejected'])
    
    # Get user's pending approvals (if admin)
    pending_approvals = []
    if current_user.is_admin:
        pending_approvals = [c for c in changes if c.status == 'pending']
    
    # Get user's submitted changes
    my_changes = [c for c in changes if c.requested_by == current_user.id]
    
    return render_template('change_control/dashboard.html',
                         changes=changes[:10],  # Recent 10
                         total_changes=total_changes,
                         pending_changes=pending_changes,
                         approved_changes=approved_changes,
                         implemented_changes=implemented_changes,
                         rejected_changes=rejected_changes,
                         pending_approvals=pending_approvals[:5],
                         my_changes=my_changes[:5],
                         title='Change Control')


@app.route('/change-control/requests')
@login_required
def change_control_list():
    """List all change requests"""
    from models import ChangeControl
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    
    # Base query
    query = ChangeControl.query
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if type_filter != 'all':
        query = query.filter_by(change_type=type_filter)
    
    # Get all changes
    changes = query.order_by(ChangeControl.requested_date.desc()).all()
    
    return render_template('change_control/list.html',
                         changes=changes,
                         status_filter=status_filter,
                         type_filter=type_filter,
                         title='Change Requests')


@app.route('/change-control/request/<int:change_id>')
@login_required
def view_change_request(change_id):
    """View change request details"""
    from models import ChangeControl
    
    change = ChangeControl.query.get_or_404(change_id)
    
    # Check if user can approve (admin only)
    can_approve = current_user.is_admin and change.status == 'pending'
    
    # Check if user can implement (admin only, approved changes)
    can_implement = current_user.is_admin and change.status == 'approved'
    
    return render_template('change_control/detail.html',
                         change=change,
                         can_approve=can_approve,
                         can_implement=can_implement,
                         title=f'Change Request {change.change_number}')


@app.route('/change-control/request/create', methods=['GET', 'POST'])
@login_required
def create_change_request():
    """Create new change request"""
    if request.method == 'POST':
        from models import ChangeControl
        
        try:
            # Get form data
            title = request.form.get('title')
            description = request.form.get('description')
            change_type = request.form.get('change_type')
            priority = request.form.get('priority')
            justification = request.form.get('justification')
            impact_assessment = request.form.get('impact_assessment')
            affected_systems = request.form.get('affected_systems')
            rollback_plan = request.form.get('rollback_plan')
            version_before = request.form.get('version_before')
            version_after = request.form.get('version_after')
            
            # Validate required fields
            if not all([title, description, change_type, priority, justification]):
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('create_change_request'))
            
            # Generate change number (CHG-YYYYMMDD-XXXX)
            from datetime import datetime
            today = datetime.utcnow().strftime('%Y%m%d')
            count = ChangeControl.query.filter(
                ChangeControl.change_number.like(f'CHG-{today}-%')
            ).count()
            change_number = f'CHG-{today}-{count+1:04d}'
            
            # Create change request
            change = ChangeControl(
                change_number=change_number,
                title=title,
                description=description,
                change_type=change_type,
                priority=priority,
                justification=justification,
                requested_by=current_user.id,
                status='pending',
                impact_assessment=impact_assessment,
                affected_systems=affected_systems,
                rollback_plan=rollback_plan,
                version_before=version_before,
                version_after=version_after
            )
            
            db.session.add(change)
            db.session.commit()
            
            # Log to blockchain
            add_to_blockchain(
                event_type='change_request_created',
                user_id=current_user.id,
                details=f'Change request {change_number} created: {title}'
            )
            
            flash(f'Change request {change_number} created successfully!', 'success')
            return redirect(url_for('view_change_request', change_id=change.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating change request: {str(e)}', 'danger')
            return redirect(url_for('create_change_request'))
    
    return render_template('change_control/create.html',
                         title='Create Change Request')


@app.route('/change-control/request/<int:change_id>/approve', methods=['GET', 'POST'])
@login_required
def approve_change_request(change_id):
    """Approve or reject change request with electronic signature"""
    from models import ChangeControl, ElectronicSignature
    
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('view_change_request', change_id=change_id))
    
    change = ChangeControl.query.get_or_404(change_id)
    
    if change.status != 'pending':
        flash('This change request has already been processed.', 'warning')
        return redirect(url_for('view_change_request', change_id=change_id))
    
    if request.method == 'POST':
        try:
            # Get form data
            action = request.form.get('action')  # 'approve' or 'reject'
            password = request.form.get('password')
            signature_reason = request.form.get('signature_reason')
            comments = request.form.get('comments')
            
            # Validate password
            if not current_user.check_password(password):
                flash('Invalid password. Electronic signature failed.', 'danger')
                return redirect(url_for('approve_change_request', change_id=change_id))
            
            # Validate required fields
            if not signature_reason:
                flash('Signature reason is required per 21 CFR §11.200(a).', 'danger')
                return redirect(url_for('approve_change_request', change_id=change_id))
            
            # Create electronic signature
            approved_date = datetime.utcnow()
            signature_data = f"{current_user.username}:{password}:{approved_date.isoformat()}:change_control_approval"
            signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
            
            signature = ElectronicSignature(
                user_id=current_user.id,
                event_type='change_control_approval',
                action=f'{action.capitalize()} change request {change.change_number}',
                reason=signature_reason,
                signature_hash=signature_hash,
                ip_address=request.remote_addr
            )
            db.session.add(signature)
            db.session.flush()
            
            # Update change request
            change.status = 'approved' if action == 'approve' else 'rejected'
            change.approved_by = current_user.id
            change.approved_date = approved_date
            change.approval_signature_id = signature.id
            if comments:
                change.description += f"\n\n--- Approval Comments ---\n{comments}"
            
            db.session.commit()
            
            # Log to blockchain
            add_to_blockchain(
                event_type='change_request_reviewed',
                user_id=current_user.id,
                details=f'Change request {change.change_number} {action}ed by {current_user.username}'
            )
            
            flash(f'Change request {change.change_number} {action}ed successfully!', 'success')
            return redirect(url_for('view_change_request', change_id=change.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing approval: {str(e)}', 'danger')
            return redirect(url_for('approve_change_request', change_id=change_id))
    
    return render_template('change_control/approve.html',
                         change=change,
                         title=f'Approve Change Request {change.change_number}')


@app.route('/change-control/request/<int:change_id>/implement', methods=['GET', 'POST'])
@login_required
def implement_change_request(change_id):
    """Mark change as implemented with electronic signature"""
    from models import ChangeControl, ElectronicSignature
    
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('view_change_request', change_id=change_id))
    
    change = ChangeControl.query.get_or_404(change_id)
    
    if change.status != 'approved':
        flash('Only approved changes can be implemented.', 'warning')
        return redirect(url_for('view_change_request', change_id=change_id))
    
    if request.method == 'POST':
        try:
            # Get form data
            password = request.form.get('password')
            signature_reason = request.form.get('signature_reason')
            implementation_notes = request.form.get('implementation_notes')
            version_after = request.form.get('version_after')
            
            # Validate password
            if not current_user.check_password(password):
                flash('Invalid password. Electronic signature failed.', 'danger')
                return redirect(url_for('implement_change_request', change_id=change_id))
            
            # Validate required fields
            if not signature_reason:
                flash('Signature reason is required per 21 CFR §11.200(a).', 'danger')
                return redirect(url_for('implement_change_request', change_id=change_id))
            
            # Create electronic signature
            implemented_date = datetime.utcnow()
            signature_data = f"{current_user.username}:{password}:{implemented_date.isoformat()}:change_implementation"
            signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
            
            signature = ElectronicSignature(
                user_id=current_user.id,
                event_type='change_implementation',
                action=f'Implemented change request {change.change_number}',
                reason=signature_reason,
                signature_hash=signature_hash,
                ip_address=request.remote_addr
            )
            db.session.add(signature)
            db.session.flush()
            
            # Update change request
            change.status = 'implemented'
            change.implemented_by = current_user.id
            change.implemented_date = implemented_date
            change.implementation_signature_id = signature.id
            if version_after:
                change.version_after = version_after
            if implementation_notes:
                change.description += f"\n\n--- Implementation Notes ---\n{implementation_notes}"
            
            db.session.commit()
            
            # Log to blockchain
            add_to_blockchain(
                event_type='change_implemented',
                user_id=current_user.id,
                details=f'Change request {change.change_number} implemented by {current_user.username}'
            )
            
            flash(f'Change request {change.change_number} marked as implemented!', 'success')
            return redirect(url_for('view_change_request', change_id=change.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording implementation: {str(e)}', 'danger')
            return redirect(url_for('implement_change_request', change_id=change_id))
    
    return render_template('change_control/implement.html',
                         change=change,
                         title=f'Implement Change Request {change.change_number}')


@app.route('/change-control/reports')
@login_required
def change_control_reports():
    """Change control reports and analytics"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('change_control_dashboard'))
    
    from models import ChangeControl
    from sqlalchemy import func, extract
    
    # Get all changes
    changes = ChangeControl.query.all()
    
    # Status breakdown
    status_stats = db.session.query(
        ChangeControl.status,
        func.count(ChangeControl.id)
    ).group_by(ChangeControl.status).all()
    
    # Type breakdown
    type_stats = db.session.query(
        ChangeControl.change_type,
        func.count(ChangeControl.id)
    ).group_by(ChangeControl.change_type).all()
    
    # Priority breakdown
    priority_stats = db.session.query(
        ChangeControl.priority,
        func.count(ChangeControl.id)
    ).group_by(ChangeControl.priority).all()
    
    # Monthly trend (last 12 months)
    monthly_stats = db.session.query(
        extract('year', ChangeControl.requested_date).label('year'),
        extract('month', ChangeControl.requested_date).label('month'),
        func.count(ChangeControl.id).label('count')
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    # Average implementation time
    implemented = ChangeControl.query.filter_by(status='implemented').all()
    avg_implementation_days = 0
    if implemented:
        total_days = sum([
            (c.implemented_date - c.requested_date).days 
            for c in implemented if c.implemented_date and c.requested_date
        ])
        avg_implementation_days = total_days / len(implemented) if len(implemented) > 0 else 0
    
    return render_template('change_control/reports.html',
                         changes=changes,
                         status_stats=dict(status_stats),
                         type_stats=dict(type_stats),
                         priority_stats=dict(priority_stats),
                         monthly_stats=monthly_stats,
                         avg_implementation_days=round(avg_implementation_days, 1),
                         title='Change Control Reports')


# ============================================================================
# VALIDATION TESTING ROUTES (21 CFR Part 11 Compliance - IQ/OQ/PQ)
# ============================================================================

@app.route('/validation')
@login_required
def validation_dashboard():
    """Validation testing dashboard"""
    from models import ValidationTest
    
    # Get all validation tests
    tests = ValidationTest.query.order_by(ValidationTest.test_number).all()
    
    # Get statistics by type
    iq_tests = [t for t in tests if t.test_type == 'IQ']
    oq_tests = [t for t in tests if t.test_type == 'OQ']
    pq_tests = [t for t in tests if t.test_type == 'PQ']
    
    # Get statistics by status
    pending_tests = [t for t in tests if t.status == 'pending']
    passed_tests = [t for t in tests if t.status == 'pass']
    failed_tests = [t for t in tests if t.status == 'fail']
    retest_tests = [t for t in tests if t.status == 'retest']
    
    # Calculate pass rate
    total_executed = len([t for t in tests if t.status in ['pass', 'fail']])
    pass_rate = (len(passed_tests) / total_executed * 100) if total_executed > 0 else 0
    
    return render_template('validation/dashboard.html',
                         tests=tests,
                         iq_tests=iq_tests,
                         oq_tests=oq_tests,
                         pq_tests=pq_tests,
                         pending_tests=pending_tests,
                         passed_tests=passed_tests,
                         failed_tests=failed_tests,
                         retest_tests=retest_tests,
                         pass_rate=round(pass_rate, 1),
                         title='Validation Testing')


@app.route('/validation/tests')
@login_required
def validation_tests():
    """List all validation tests"""
    from models import ValidationTest
    
    # Get filter parameters
    test_type = request.args.get('type', 'all')
    status = request.args.get('status', 'all')
    
    # Base query
    query = ValidationTest.query
    
    # Apply filters
    if test_type != 'all':
        query = query.filter_by(test_type=test_type)
    if status != 'all':
        query = query.filter_by(status=status)
    
    tests = query.order_by(ValidationTest.test_number).all()
    
    return render_template('validation/tests.html',
                         tests=tests,
                         test_type=test_type,
                         status=status,
                         title='Validation Tests')


@app.route('/validation/test/<int:test_id>')
@login_required
def view_validation_test(test_id):
    """View validation test details"""
    from models import ValidationTest
    
    test = ValidationTest.query.get_or_404(test_id)
    
    # Check if user can execute (admin or assigned tester)
    can_execute = current_user.is_admin and test.status in ['pending', 'retest']
    
    # Check if user can review (admin only, executed tests)
    can_review = current_user.is_admin and test.status in ['pass', 'fail'] and not test.reviewed_by
    
    return render_template('validation/detail.html',
                         test=test,
                         can_execute=can_execute,
                         can_review=can_review,
                         title=f'{test.test_number}')


@app.route('/validation/test/create', methods=['GET', 'POST'])
@login_required
def create_validation_test():
    """Create new validation test"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('validation_dashboard'))
    
    if request.method == 'POST':
        from models import ValidationTest
        
        try:
            # Get form data
            test_type = request.form.get('test_type')
            test_number = request.form.get('test_number')
            test_name = request.form.get('test_name')
            description = request.form.get('description')
            test_category = request.form.get('test_category')
            
            # Equipment information
            equipment_name = request.form.get('equipment_name')
            equipment_model = request.form.get('equipment_model')
            equipment_serial = request.form.get('equipment_serial')
            
            # Test procedure
            prerequisites = request.form.get('prerequisites')
            procedure = request.form.get('procedure')
            expected_result = request.form.get('expected_result')
            acceptance_criteria = request.form.get('acceptance_criteria')
            
            # Metadata
            system_version = request.form.get('system_version')
            test_environment = request.form.get('test_environment')
            
            # Validate required fields
            if not all([test_type, test_number, test_name, test_category, 
                       equipment_name, equipment_model, equipment_serial,
                       procedure, expected_result, acceptance_criteria]):
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('create_validation_test'))
            
            # Create validation test
            test = ValidationTest(
                test_number=test_number,
                test_type=test_type,
                test_name=test_name,
                description=description,
                test_category=test_category,
                equipment_name=equipment_name,
                equipment_model=equipment_model,
                equipment_serial=equipment_serial,
                prerequisites=prerequisites,
                procedure=procedure,
                expected_result=expected_result,
                acceptance_criteria=acceptance_criteria,
                system_version=system_version,
                test_environment=test_environment,
                status='pending'
            )
            
            db.session.add(test)
            db.session.commit()
            
            # Log to blockchain
            add_to_blockchain(
                event_type='validation_test_created',
                user_id=current_user.id,
                details=f'Validation test {test_number} created: {test_name}'
            )
            
            flash(f'Validation test {test_number} created successfully!', 'success')
            return redirect(url_for('view_validation_test', test_id=test.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating validation test: {str(e)}', 'danger')
            return redirect(url_for('create_validation_test'))
    
    return render_template('validation/create.html',
                         title='Create Validation Test')


@app.route('/validation/test/<int:test_id>/execute', methods=['GET', 'POST'])
@login_required
def execute_validation_test(test_id):
    """Execute validation test with electronic signature"""
    from models import ValidationTest, ElectronicSignature
    
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('view_validation_test', test_id=test_id))
    
    test = ValidationTest.query.get_or_404(test_id)
    
    if test.status not in ['pending', 'retest']:
        flash('This test has already been executed.', 'warning')
        return redirect(url_for('view_validation_test', test_id=test_id))
    
    if request.method == 'POST':
        try:
            # Get form data
            actual_result = request.form.get('actual_result')
            status = request.form.get('status')  # 'pass' or 'fail'
            notes = request.form.get('notes')
            password = request.form.get('password')
            signature_reason = request.form.get('signature_reason')
            
            # Validate password
            if not current_user.check_password(password):
                flash('Invalid password. Electronic signature failed.', 'danger')
                return redirect(url_for('execute_validation_test', test_id=test_id))
            
            # Validate required fields
            if not all([actual_result, status, signature_reason]):
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('execute_validation_test', test_id=test_id))
            
            # Create electronic signature
            executed_date = datetime.utcnow()
            signature_data = f"{current_user.username}:{password}:{executed_date.isoformat()}:validation_execution"
            signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
            
            signature = ElectronicSignature(
                user_id=current_user.id,
                event_type='validation_execution',
                action=f'Executed validation test {test.test_number}',
                reason=signature_reason,
                signature_hash=signature_hash,
                ip_address=request.remote_addr
            )
            db.session.add(signature)
            db.session.flush()
            
            # Update test
            test.actual_result = actual_result
            test.status = status
            test.executed_by = current_user.id
            test.executed_date = executed_date
            test.execution_signature_id = signature.id
            if notes:
                test.notes = notes
            
            db.session.commit()
            
            # Log to blockchain
            add_to_blockchain(
                event_type='validation_test_executed',
                user_id=current_user.id,
                details=f'Validation test {test.test_number} executed with result: {status}'
            )
            
            flash(f'Validation test {test.test_number} executed successfully!', 'success')
            return redirect(url_for('view_validation_test', test_id=test.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error executing test: {str(e)}', 'danger')
            return redirect(url_for('execute_validation_test', test_id=test_id))
    
    return render_template('validation/execute.html',
                         test=test,
                         title=f'Execute {test.test_number}')


@app.route('/validation/test/<int:test_id>/review', methods=['GET', 'POST'])
@login_required
def review_validation_test(test_id):
    """Review validation test results with electronic signature"""
    from models import ValidationTest, ElectronicSignature
    
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('view_validation_test', test_id=test_id))
    
    test = ValidationTest.query.get_or_404(test_id)
    
    if test.status not in ['pass', 'fail']:
        flash('Only executed tests can be reviewed.', 'warning')
        return redirect(url_for('view_validation_test', test_id=test_id))
    
    if test.reviewed_by:
        flash('This test has already been reviewed.', 'warning')
        return redirect(url_for('view_validation_test', test_id=test_id))
    
    if request.method == 'POST':
        try:
            # Get form data
            password = request.form.get('password')
            signature_reason = request.form.get('signature_reason')
            review_comments = request.form.get('review_comments')
            action = request.form.get('action')  # 'approve' or 'retest'
            
            # Validate password
            if not current_user.check_password(password):
                flash('Invalid password. Electronic signature failed.', 'danger')
                return redirect(url_for('review_validation_test', test_id=test_id))
            
            # Validate required fields
            if not signature_reason:
                flash('Signature reason is required per 21 CFR §11.200(a).', 'danger')
                return redirect(url_for('review_validation_test', test_id=test_id))
            
            # Create electronic signature
            reviewed_date = datetime.utcnow()
            signature_data = f"{current_user.username}:{password}:{reviewed_date.isoformat()}:validation_review"
            signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
            
            signature = ElectronicSignature(
                user_id=current_user.id,
                event_type='validation_review',
                action=f'Reviewed validation test {test.test_number}',
                reason=signature_reason,
                signature_hash=signature_hash,
                ip_address=request.remote_addr
            )
            db.session.add(signature)
            db.session.flush()
            
            # Update test
            test.reviewed_by = current_user.id
            test.reviewed_date = reviewed_date
            test.review_signature_id = signature.id
            if review_comments:
                test.notes = (test.notes or '') + f"\n\n--- Review Comments ---\n{review_comments}"
            
            # Handle retest action
            if action == 'retest':
                test.status = 'retest'
                test.reviewed_by = None
                test.reviewed_date = None
                test.review_signature_id = None
            
            db.session.commit()
            
            # Log to blockchain
            add_to_blockchain(
                event_type='validation_test_reviewed',
                user_id=current_user.id,
                details=f'Validation test {test.test_number} reviewed by {current_user.username}'
            )
            
            flash(f'Validation test {test.test_number} reviewed successfully!', 'success')
            return redirect(url_for('view_validation_test', test_id=test.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error reviewing test: {str(e)}', 'danger')
            return redirect(url_for('review_validation_test', test_id=test_id))
    
    return render_template('validation/review.html',
                         test=test,
                         title=f'Review {test.test_number}')


@app.route('/validation/reports')
@login_required
def validation_reports():
    """Validation testing reports and metrics"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('validation_dashboard'))
    
    from models import ValidationTest
    from sqlalchemy import func
    from datetime import datetime
    
    # Check for CSV export
    if request.args.get('export') == 'csv':
        import csv
        from io import StringIO
        from flask import make_response
        
        tests = ValidationTest.query.all()
        
        # Create CSV
        si = StringIO()
        writer = csv.writer(si)
        
        # Write headers
        writer.writerow([
            'Test Number', 'Test Name', 'Type', 'Status', 
            'System Version', 'Environment', 'Executed By', 
            'Executed Date', 'Reviewed By', 'Reviewed Date',
            'Expected Result', 'Actual Result', 'Notes'
        ])
        
        # Write data
        for test in tests:
            writer.writerow([
                test.test_number,
                test.test_name,
                test.test_type,
                test.status,
                test.system_version or '',
                test.test_environment or '',
                test.executor.username if test.executor else '',
                test.executed_date.strftime('%Y-%m-%d %H:%M:%S') if test.executed_date else '',
                test.reviewer.username if test.reviewer else '',
                test.reviewed_date.strftime('%Y-%m-%d %H:%M:%S') if test.reviewed_date else '',
                test.expected_result or '',
                test.actual_result or '',
                test.notes or ''
            ])
        
        # Create response
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename=validation_tests_{datetime.now().strftime('%Y%m%d')}.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    
    # Get all tests
    tests = ValidationTest.query.all()
    
    # Overall statistics
    total_tests = len(tests)
    tests_passed = ValidationTest.query.filter_by(status='pass').count()
    tests_failed = ValidationTest.query.filter_by(status='fail').count()
    pending_tests = ValidationTest.query.filter_by(status='pending').count()
    retest_tests = ValidationTest.query.filter_by(status='retest').count()
    
    total_executed = tests_passed + tests_failed
    pass_rate = round((tests_passed / total_executed * 100) if total_executed > 0 else 0)
    
    # Type-specific statistics
    iq_total = ValidationTest.query.filter_by(test_type='IQ').count()
    iq_passed = ValidationTest.query.filter_by(test_type='IQ', status='pass').count()
    iq_failed = ValidationTest.query.filter_by(test_type='IQ', status='fail').count()
    iq_pending = ValidationTest.query.filter_by(test_type='IQ', status='pending').count()
    iq_executed = iq_passed + iq_failed
    iq_pass_rate = round((iq_passed / iq_executed * 100) if iq_executed > 0 else 0)
    
    oq_total = ValidationTest.query.filter_by(test_type='OQ').count()
    oq_passed = ValidationTest.query.filter_by(test_type='OQ', status='pass').count()
    oq_failed = ValidationTest.query.filter_by(test_type='OQ', status='fail').count()
    oq_pending = ValidationTest.query.filter_by(test_type='OQ', status='pending').count()
    oq_executed = oq_passed + oq_failed
    oq_pass_rate = round((oq_passed / oq_executed * 100) if oq_executed > 0 else 0)
    
    pq_total = ValidationTest.query.filter_by(test_type='PQ').count()
    pq_passed = ValidationTest.query.filter_by(test_type='PQ', status='pass').count()
    pq_failed = ValidationTest.query.filter_by(test_type='PQ', status='fail').count()
    pq_pending = ValidationTest.query.filter_by(test_type='PQ', status='pending').count()
    pq_executed = pq_passed + pq_failed
    pq_pass_rate = round((pq_passed / pq_executed * 100) if pq_executed > 0 else 0)
    
    # Electronic signature counts
    execution_signatures = ValidationTest.query.filter(ValidationTest.execution_signature_id.isnot(None)).count()
    review_signatures = ValidationTest.query.filter(ValidationTest.review_signature_id.isnot(None)).count()
    
    # Recent test activity
    recent_tests = ValidationTest.query.order_by(ValidationTest.executed_date.desc()).limit(10).all()
    
    return render_template('validation/reports.html',
                         total_tests=total_tests,
                         tests_passed=tests_passed,
                         tests_failed=tests_failed,
                         pending_tests=pending_tests,
                         passed_tests=tests_passed,
                         failed_tests=tests_failed,
                         retest_tests=retest_tests,
                         pass_rate=pass_rate,
                         iq_total=iq_total,
                         iq_passed=iq_passed,
                         iq_failed=iq_failed,
                         iq_pending=iq_pending,
                         iq_pass_rate=iq_pass_rate,
                         oq_total=oq_total,
                         oq_passed=oq_passed,
                         oq_failed=oq_failed,
                         oq_pending=oq_pending,
                         oq_pass_rate=oq_pass_rate,
                         pq_total=pq_total,
                         pq_passed=pq_passed,
                         pq_failed=pq_failed,
                         pq_pending=pq_pending,
                         pq_pass_rate=pq_pass_rate,
                         execution_signatures=execution_signatures,
                         review_signatures=review_signatures,
                         recent_tests=recent_tests,
                         now=datetime.now(),
                         title='Validation Reports')


# ==================== IQ/OQ/PQ PDF Template Export Routes ====================

@app.route('/validation/export/iq-template')
@login_required
def export_iq_template():
    """Generate and download IQ PDF template"""
    from validation_pdf_templates import generate_iq_template_pdf
    from models import CompanyProfile, DoorSystemInfo
    from flask import send_file
    
    # Get company info
    company = CompanyProfile.query.first()
    company_info = {
        'company_name': company.company_name if company else 'Your Company Name',
        'address': company.company_address if company else '',
        'email': company.company_email if company else '',
        'phone': company.company_phone if company else ''
    }
    
    # Get equipment info
    door_system = DoorSystemInfo.query.first()
    equipment_info = {
        'name': 'eDOMOS Door Monitoring System',
        'model': door_system.system_model if door_system else 'eDOMOS-2.1-Pro',
        'serial': door_system.device_serial_number if door_system else 'N/A',
        'version': 'v2.1.0'
    }
    
    # Customer info (optional - can be filled manually)
    customer_info = {
        'customer_name': '',
        'department': door_system.department_name if door_system else '',
        'site': door_system.door_location if door_system else ''
    }
    
    # Generate PDF
    pdf_buffer = generate_iq_template_pdf(equipment_info, company_info, customer_info)
    
    # Log activity
    add_to_blockchain(
        event_type='iq_template_exported',
        user_id=current_user.id,
        details=f'IQ template PDF exported by {current_user.username}'
    )
    
    # Send file
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'IQ_Template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


@app.route('/validation/export/oq-template')
@login_required
def export_oq_template():
    """Generate and download OQ PDF template"""
    from validation_pdf_templates import generate_oq_template_pdf
    from models import CompanyProfile, DoorSystemInfo
    from flask import send_file
    
    # Get company info
    company = CompanyProfile.query.first()
    company_info = {
        'company_name': company.company_name if company else 'Your Company Name',
        'address': company.company_address if company else '',
        'email': company.company_email if company else '',
        'phone': company.company_phone if company else ''
    }
    
    # Get equipment info
    door_system = DoorSystemInfo.query.first()
    equipment_info = {
        'name': 'eDOMOS Door Monitoring System',
        'model': door_system.system_model if door_system else 'eDOMOS-2.1-Pro',
        'serial': door_system.device_serial_number if door_system else 'N/A',
        'version': 'v2.1.0'
    }
    
    # Generate PDF
    pdf_buffer = generate_oq_template_pdf(equipment_info, company_info)
    
    # Log activity
    add_to_blockchain(
        event_type='oq_template_exported',
        user_id=current_user.id,
        details=f'OQ template PDF exported by {current_user.username}'
    )
    
    # Send file
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'OQ_Template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


@app.route('/validation/export/pq-template')
@login_required
def export_pq_template():
    """Generate and download PQ PDF template"""
    from validation_pdf_templates import generate_pq_template_pdf
    from models import CompanyProfile, DoorSystemInfo
    from flask import send_file
    
    # Get company info
    company = CompanyProfile.query.first()
    company_info = {
        'company_name': company.company_name if company else 'Your Company Name',
        'address': company.company_address if company else '',
        'email': company.company_email if company else '',
        'phone': company.company_phone if company else ''
    }
    
    # Get equipment info
    door_system = DoorSystemInfo.query.first()
    equipment_info = {
        'name': 'eDOMOS Door Monitoring System',
        'model': door_system.system_model if door_system else 'eDOMOS-2.1-Pro',
        'serial': door_system.device_serial_number if door_system else 'N/A',
        'version': 'v2.1.0'
    }
    
    # Generate PDF
    pdf_buffer = generate_pq_template_pdf(equipment_info, company_info)
    
    # Log activity
    add_to_blockchain(
        event_type='pq_template_exported',
        user_id=current_user.id,
        details=f'PQ template PDF exported by {current_user.username}'
    )
    
    # Send file
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'PQ_Template_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


# ==================== End of IQ/OQ/PQ PDF Exports ====================


# ==================== Validation Document Upload & Management ====================

@app.route('/validation/upload', methods=['POST'])
@login_required
def upload_validation_document():
    """Upload completed IQ/OQ/PQ PDF document"""
    from models import ValidationDocument, DoorSystemInfo
    from werkzeug.utils import secure_filename
    import os
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type (PDF only)
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'message': 'Only PDF files are allowed'}), 400
        
        # Get form data
        document_type = request.form.get('document_type', 'IQ')
        description = request.form.get('description', '')
        
        # Validate document type
        if document_type not in ['IQ', 'OQ', 'PQ']:
            return jsonify({'success': False, 'message': 'Invalid document type'}), 400
        
        # Get system metadata
        equipment = DoorSystemInfo.query.first()
        system_id = equipment.device_serial_number if equipment else 'N/A'
        software_version = 'v2.1.0'  # eDOMOS version
        site_location = equipment.door_location if equipment else 'N/A'
        
        # Generate unique document number
        doc_count = ValidationDocument.query.filter_by(document_type=document_type).count()
        document_number = f'VDOC-{document_type}-{datetime.now().strftime("%Y%m%d")}-{doc_count + 1:03d}'
        
        # Secure filename and save
        original_filename = secure_filename(file.filename)
        filename = f'{document_number}_{original_filename}'
        upload_folder = os.path.join(os.path.dirname(__file__), 'uploads', 'validation_docs')
        file_path = os.path.join(upload_folder, filename)
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Create database record
        doc = ValidationDocument(
            document_number=document_number,
            document_type=document_type,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            system_id=system_id,
            software_version=software_version,
            site_location=site_location,
            uploaded_by=current_user.id,
            uploaded_at=datetime.utcnow(),
            status='pending',
            description=description
        )
        
        db.session.add(doc)
        db.session.commit()
        
        # Log to blockchain
        try:
            add_blockchain_event(
                event_type='validation_document_uploaded',
                user_id=current_user.id,
                details=f'{document_type} document uploaded: {document_number}'
            )
        except Exception as e:
            print(f"[BLOCKCHAIN WARNING] Failed to log upload: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'document': doc.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Upload failed: {e}")
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'}), 500


@app.route('/validation/documents')
@login_required
def validation_documents():
    """View all uploaded validation documents"""
    from models import ValidationDocument
    
    # Get all documents, ordered by upload date (newest first)
    documents = ValidationDocument.query.order_by(ValidationDocument.uploaded_at.desc()).all()
    
    # Filter by type if specified
    doc_type = request.args.get('type')
    if doc_type and doc_type in ['IQ', 'OQ', 'PQ']:
        documents = [d for d in documents if d.document_type == doc_type]
    
    # Filter by status if specified
    status = request.args.get('status')
    if status and status in ['pending', 'submitted', 'approved', 'rejected', 'archived']:
        documents = [d for d in documents if d.status == status]
    
    # Count by status
    pending_count = ValidationDocument.query.filter_by(status='pending').count()
    submitted_count = ValidationDocument.query.filter_by(status='submitted').count()
    approved_count = ValidationDocument.query.filter_by(status='approved').count()
    rejected_count = ValidationDocument.query.filter_by(status='rejected').count()
    
    return render_template('validation/documents.html',
                         documents=documents,
                         pending_count=pending_count,
                         submitted_count=submitted_count,
                         approved_count=approved_count,
                         rejected_count=rejected_count,
                         title='Validation Documents')


@app.route('/validation/document/<int:doc_id>')
@login_required
def view_validation_document(doc_id):
    """View a specific validation document"""
    from models import ValidationDocument
    
    doc = ValidationDocument.query.get_or_404(doc_id)
    
    return render_template('validation/document_detail.html',
                         document=doc,
                         title=f'Document: {doc.document_number}')


@app.route('/validation/document/<int:doc_id>/download')
@login_required
def download_validation_document(doc_id):
    """Download uploaded validation document"""
    from models import ValidationDocument
    import os
    
    doc = ValidationDocument.query.get_or_404(doc_id)
    
    # Check if file exists
    if not os.path.exists(doc.file_path):
        flash('File not found', 'error')
        return redirect(url_for('validation_documents'))
    
    # Log download to blockchain
    try:
        add_blockchain_event(
            event_type='validation_document_downloaded',
            user_id=current_user.id,
            details=f'Downloaded {doc.document_type} document: {doc.document_number}'
        )
    except Exception as e:
        print(f"[BLOCKCHAIN WARNING] Failed to log download: {e}")
    
    return send_file(
        doc.file_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=doc.original_filename
    )


@app.route('/validation/document/<int:doc_id>/approve', methods=['POST'])
@login_required
def approve_validation_document(doc_id):
    """Approve a validation document (Admin/QA only)"""
    from models import ValidationDocument
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    doc = ValidationDocument.query.get_or_404(doc_id)
    
    # Update status to approved
    doc.status = 'approved'
    doc.approved_by = current_user.id
    doc.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log to blockchain
    try:
        add_blockchain_event(
            event_type='validation_document_approved',
            user_id=current_user.id,
            details=f'Approved {doc.document_type} document: {doc.document_number}'
        )
    except Exception as e:
        print(f"[BLOCKCHAIN WARNING] Failed to log approval: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Document approved successfully',
        'document': doc.to_dict()
    })


@app.route('/validation/document/<int:doc_id>/reject', methods=['POST'])
@login_required
def reject_validation_document(doc_id):
    """Reject a validation document (Admin/QA only)"""
    from models import ValidationDocument
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    doc = ValidationDocument.query.get_or_404(doc_id)
    
    # Get rejection reason
    data = request.get_json()
    rejection_reason = data.get('reason', 'No reason provided')
    
    # Update status to rejected
    doc.status = 'rejected'
    doc.rejection_reason = rejection_reason
    doc.approved_by = current_user.id
    doc.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log to blockchain
    try:
        add_blockchain_event(
            event_type='validation_document_rejected',
            user_id=current_user.id,
            details=f'Rejected {doc.document_type} document: {doc.document_number} - {rejection_reason}'
        )
    except Exception as e:
        print(f"[BLOCKCHAIN WARNING] Failed to log rejection: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Document rejected',
        'document': doc.to_dict()
    })


@app.route('/validation/document/<int:doc_id>/submit', methods=['POST'])
@login_required
def submit_validation_document(doc_id):
    """Submit document for approval"""
    from models import ValidationDocument
    
    doc = ValidationDocument.query.get_or_404(doc_id)
    
    # Only uploader can submit
    if doc.uploaded_by != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Not authorized'}), 403
    
    # Update status to submitted
    doc.status = 'submitted'
    doc.submitted_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log to blockchain
    try:
        add_blockchain_event(
            event_type='validation_document_submitted',
            user_id=current_user.id,
            details=f'Submitted {doc.document_type} document for approval: {doc.document_number}'
        )
    except Exception as e:
        print(f"[BLOCKCHAIN WARNING] Failed to log submission: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Document submitted for approval',
        'document': doc.to_dict()
    })


# ==================== End of Validation Document Management ====================


@app.route('/dashboard')
@login_required
def dashboard():
    # Get user permissions
    permissions = current_user.permissions.split(',') if current_user.permissions else ['dashboard']
    
    # Get system status
    door_status = "Open" if door_open else "Closed"
    alarm_status = "Active" if alarm_active else "Inactive"
    timer_set = Setting.query.filter_by(key='timer_duration').first().value
    
    # Get event counts
    total_events = EventLog.query.count()
    door_open_events = EventLog.query.filter_by(event_type='door_open').count()
    door_close_events = EventLog.query.filter_by(event_type='door_close').count()
    alarm_events = EventLog.query.filter_by(event_type='alarm_triggered').count()
    
    # Get last event
    last_event = EventLog.query.order_by(EventLog.timestamp.desc()).first()
    last_event_str = last_event.to_dict() if last_event else None
    
    # Get system uptime
    uptime_data = calculate_uptime()
    
    # Use original dashboard
    return render_template('dashboard.html', 
        permissions=permissions,
        door_status=door_status,
        alarm_status=alarm_status,
        timer_set=timer_set,
        total_events=total_events,
        door_open_events=door_open_events,
        door_close_events=door_close_events,
        alarm_events=alarm_events,
        last_event=last_event_str,
        uptime=uptime_data
    )

@app.route('/event-log')
@login_required
def event_log():
    """Display full event log page"""
    if 'event_log' not in current_user.permissions.split(','):
        return redirect(url_for('dashboard'))
    
    from models import UserPreference
    
    # Get user preferences for date/time formatting
    user_pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    date_format = user_pref.date_format if user_pref and user_pref.date_format else 'YYYY-MM-DD'
    time_format = user_pref.time_format if user_pref and user_pref.time_format else '24h'
    
    # Get all events with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50
    events = EventLog.query.order_by(EventLog.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('event_log.html', 
        events=events.items,
        pagination=events,
        permissions=current_user.permissions.split(','),
        user_date_format=date_format,
        user_time_format=time_format
    )

@app.route('/admin/onboarding', methods=['GET', 'POST'])
@login_required
def admin_onboarding():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    # Check if already configured
    email_config = EmailConfig.query.first()
    if email_config and email_config.is_configured:
        return redirect(url_for('admin_panel'))
        
    form = AdminSettingsForm()
    if form.validate_on_submit():
        # Save email configuration
        email_config = EmailConfig.query.first()
        if not email_config:
            email_config = EmailConfig()
            
        email_config.sender_email = form.sender_email.data
        email_config.app_password = form.app_password.data
        email_config.recipient_emails = form.recipient_emails.data
        email_config.is_configured = True
        
        db.session.add(email_config)
        
        # Save timer setting
        timer_setting = Setting.query.filter_by(key='timer_duration').first()
        if timer_setting:
            timer_setting.value = str(form.timer_duration.data)
        else:
            timer_setting = Setting(key='timer_duration', value=str(form.timer_duration.data))
            db.session.add(timer_setting)
            
        db.session.commit()
        return redirect(url_for('admin_panel'))
        
    return render_template('admin_onboarding.html', form=form)

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    create_form = CreateUserForm()
    settings_form = AdminSettingsForm()
    
    # Pre-fill settings form
    timer_setting = Setting.query.filter_by(key='timer_duration').first()
    email_config = EmailConfig.query.first()
    bh_start_setting = Setting.query.filter_by(key='business_hours_start').first()
    bh_end_setting = Setting.query.filter_by(key='business_hours_end').first()
    
    if timer_setting:
        settings_form.timer_duration.data = int(timer_setting.value)
    if email_config:
        settings_form.sender_email.data = email_config.sender_email
        settings_form.app_password.data = email_config.app_password
        settings_form.recipient_emails.data = email_config.recipient_emails
    
    # Convert business hours to HH:MM format
    business_hours_start = f"{int(bh_start_setting.value):02d}:00" if bh_start_setting else "09:00"
    business_hours_end = f"{int(bh_end_setting.value):02d}:00" if bh_end_setting else "17:00"
    
    return render_template('admin_streamlined.html', 
        users=users, 
        create_form=create_form, 
        settings_form=settings_form,
        business_hours_start=business_hours_start,
        business_hours_end=business_hours_end,
        permissions=current_user.permissions.split(',')
    )

@app.route('/admin/create-user', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash('Permission denied', 'error')
        return redirect(url_for('admin_panel'))
    
    form = CreateUserForm()
    
    # Debug form data
    print(f"Form data received: {request.form}")
    print(f"Form keys: {list(request.form.keys())}")
    print(f"Permissions received: {request.form.getlist('permissions')}")
    
    # Try different ways to get permissions
    permissions_wtf = form.permissions.data if form.permissions.data else []
    permissions_direct = request.form.getlist('permissions')
    
    print(f"WTF Permissions: {permissions_wtf}")
    print(f"Direct permissions: {permissions_direct}")
    
    # Manual validation approach to handle permission selection better
    username = form.username.data
    password = form.password.data
    is_admin = form.is_admin.data
    
    # Use WTF form data first, fallback to direct request
    permissions = permissions_wtf if permissions_wtf else permissions_direct
    
    # Basic validation
    validation_errors = []
    if not username or len(username) < 4:
        validation_errors.append('Username must be at least 4 characters long')
    if not password or len(password) < 6:
        validation_errors.append('Password must be at least 6 characters long')
    if not permissions:
        validation_errors.append('Please select at least one permission for the user')
    
    if not validation_errors:
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f'User {username} already exists', 'error')
            return redirect(url_for('admin_panel'))
        
        try:
            # Create new user
            new_user = User(
                username=username,
                is_admin=is_admin,
                permissions=','.join(permissions) if permissions else 'dashboard'
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            log_event('user_created', f'User {username} created by admin')
            flash(f'User {username} created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
    else:
        # Validation failed
        for error in validation_errors:
            flash(error, 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/settings', methods=['POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    try:
        form = AdminSettingsForm()
        if form.validate_on_submit():
            # Save email configuration
            email_config = EmailConfig.query.first()
            if not email_config:
                email_config = EmailConfig()
                
            email_config.sender_email = form.sender_email.data
            email_config.app_password = form.app_password.data
            email_config.recipient_emails = form.recipient_emails.data
            email_config.is_configured = True
            
            db.session.add(email_config)
            
            # Save timer setting
            timer_setting = Setting.query.filter_by(key='timer_duration').first()
            if timer_setting:
                timer_setting.value = str(form.timer_duration.data)
            else:
                timer_setting = Setting(key='timer_duration', value=str(form.timer_duration.data))
                db.session.add(timer_setting)
            
            # Save business hours settings if provided
            if 'business_hours_start' in request.form:
                bh_start = request.form.get('business_hours_start')
                try:
                    hour = int(bh_start.split(':')[0])
                    bh_start_setting = Setting.query.filter_by(key='business_hours_start').first()
                    if bh_start_setting:
                        bh_start_setting.value = str(hour)
                    else:
                        bh_start_setting = Setting(key='business_hours_start', value=str(hour))
                        db.session.add(bh_start_setting)
                except:
                    pass
            
            if 'business_hours_end' in request.form:
                bh_end = request.form.get('business_hours_end')
                try:
                    hour = int(bh_end.split(':')[0])
                    bh_end_setting = Setting.query.filter_by(key='business_hours_end').first()
                    if bh_end_setting:
                        bh_end_setting.value = str(hour)
                    else:
                        bh_end_setting = Setting(key='business_hours_end', value=str(hour))
                        db.session.add(bh_end_setting)
                except:
                    pass
                
            db.session.commit()
            log_event('settings_changed', 'Admin updated system settings')
        else:
            # If form did not validate, collect errors and flash to user
            if form.errors:
                for field, errs in form.errors.items():
                    for err in errs:
                        flash(f"{field}: {err}", 'error')
    except Exception as e:
        # Rollback and log full traceback without exposing internals to the user
        db.session.rollback()
        import traceback
        tb = traceback.format_exc()
        print(f"[ERROR] Exception in admin_settings: {e}\n{tb}")
        flash('An unexpected error occurred while saving settings. See server logs for details.', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/api/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Permission denied'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'PUT':
        data = request.get_json()
        user.is_admin = data.get('is_admin', False)
        user.permissions = data.get('permissions', '')
        db.session.commit()
        log_event('user_updated', f'User {user.username} permissions updated by admin')
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        if user.username == 'admin':
            return jsonify({'error': 'Cannot delete admin user'}), 403
        username = user.username
        db.session.delete(user)
        db.session.commit()
        log_event('user_deleted', f'User {username} deleted by admin')
        return jsonify({'success': True})

@app.route('/analytics')
@login_required
def analytics():
    if 'analytics' not in current_user.permissions.split(','):
        return redirect(url_for('dashboard'))
    
    # Get time range from request (default: last 30 days)
    time_range = request.args.get('range', 'month')
    
    from sqlalchemy import func, and_, case
    
    today = date.today()
    if time_range == 'day':
        start_date = today
    elif time_range == 'week':
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)
    
    # Get all door open and close events with timestamps
    door_events = EventLog.query.filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type.in_(['door_open', 'door_close'])
        )
    ).order_by(EventLog.timestamp.asc()).all()
    
    # Calculate door usage analytics
    door_open_count_day = 0
    door_open_count_week = 0
    door_open_count_month = 0
    door_open_durations = []
    open_time_total = 0
    closed_time_total = 0
    
    # Duration distribution buckets (in seconds)
    duration_buckets = {
        '0-5s': 0,
        '5-10s': 0,
        '10-30s': 0,
        '30-60s': 0,
        '1-2min': 0,
        '2-5min': 0,
        '5-10min': 0,
        '10+min': 0
    }
    
    # Process door events to calculate open durations
    last_open_time = None
    for event in door_events:
        if event.event_type == 'door_open':
            last_open_time = event.timestamp
            
            # Count opens by time range
            event_date = event.timestamp.date()
            if event_date == today:
                door_open_count_day += 1
            if event_date >= today - timedelta(days=7):
                door_open_count_week += 1
            if event_date >= today - timedelta(days=30):
                door_open_count_month += 1
                
        elif event.event_type == 'door_close' and last_open_time:
            # Calculate duration
            duration = (event.timestamp - last_open_time).total_seconds()
            door_open_durations.append(duration)
            open_time_total += duration
            
            # Categorize into buckets
            if duration < 5:
                duration_buckets['0-5s'] += 1
            elif duration < 10:
                duration_buckets['5-10s'] += 1
            elif duration < 30:
                duration_buckets['10-30s'] += 1
            elif duration < 60:
                duration_buckets['30-60s'] += 1
            elif duration < 120:
                duration_buckets['1-2min'] += 1
            elif duration < 300:
                duration_buckets['2-5min'] += 1
            elif duration < 600:
                duration_buckets['5-10min'] += 1
            else:
                duration_buckets['10+min'] += 1
            
            last_open_time = None
    
    # Calculate statistics
    total_monitoring_time = (datetime.now() - datetime.combine(start_date, datetime.min.time())).total_seconds()
    closed_time_total = total_monitoring_time - open_time_total
    
    avg_open_duration = sum(door_open_durations) / len(door_open_durations) if door_open_durations else 0
    max_open_duration = max(door_open_durations) if door_open_durations else 0
    
    # Calculate percentages
    open_percentage = (open_time_total / total_monitoring_time * 100) if total_monitoring_time > 0 else 0
    closed_percentage = 100 - open_percentage
    
    # Get daily open counts for the period
    daily_opens = db.session.query(
        func.date(EventLog.timestamp).label('date'),
        func.count(EventLog.id).label('count')
    ).filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type == 'door_open'
        )
    ).group_by(func.date(EventLog.timestamp)).all()
    
    # ============================================
    # ALARM EVENT ANALYSIS
    # ============================================
    
    # Get all alarm events in the time range
    alarm_events = EventLog.query.filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type == 'alarm_triggered'
        )
    ).order_by(EventLog.timestamp.asc()).all()
    
    # Total alarms triggered
    total_alarms = len(alarm_events)
    
    # Get timer threshold from settings
    timer_setting = Setting.query.filter_by(key='timer_duration').first()
    alarm_threshold = int(timer_setting.value) if timer_setting else 30
    
    # Calculate alarm durations (time from alarm trigger to door close)
    alarm_durations = []
    longest_alarm_duration = 0
    unacknowledged_alarms = 0
    response_times = []  # For acknowledgement response time trend
    
    # MTTR calculation (Mean Time To Resolve - alarm to door closure)
    mttr_durations = []
    
    # Compliance tracking (door events within allowed duration)
    compliant_events = 0
    non_compliant_events = 0
    
    for alarm_event in alarm_events:
        alarm_time = alarm_event.timestamp
        
        # Find the next door_close event after this alarm
        next_close = EventLog.query.filter(
            and_(
                EventLog.timestamp > alarm_time,
                EventLog.event_type == 'door_close'
            )
        ).order_by(EventLog.timestamp.asc()).first()
        
        if next_close:
            alarm_duration = (next_close.timestamp - alarm_time).total_seconds()
            alarm_durations.append(alarm_duration)
            mttr_durations.append(alarm_duration)
            
            if alarm_duration > longest_alarm_duration:
                longest_alarm_duration = alarm_duration
            
            # For response time trend: assume alarm acknowledgment happens when door is closed
            # (In a real system, you'd track explicit acknowledgments)
            response_times.append({
                'timestamp': alarm_time,
                'response_time': alarm_duration
            })
            
            # Check if alarm was resolved within threshold (2x timer for warning)
            if alarm_duration <= (alarm_threshold * 2):
                compliant_events += 1
            else:
                non_compliant_events += 1
                unacknowledged_alarms += 1  # Count as unacknowledged if took too long
        else:
            # No door close found - alarm still active or unresolved
            unacknowledged_alarms += 1
            non_compliant_events += 1
    
    # Calculate average alarm duration
    avg_alarm_duration = sum(alarm_durations) / len(alarm_durations) if alarm_durations else 0
    
    # Calculate daily alarm counts for trend analysis
    daily_alarms = db.session.query(
        func.date(EventLog.timestamp).label('date'),
        func.count(EventLog.id).label('count')
    ).filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type == 'alarm_triggered'
        )
    ).group_by(func.date(EventLog.timestamp)).all()
    
    # Weekly alarm comparison for reduction trend
    week_1_alarms = 0
    week_2_alarms = 0
    week_3_alarms = 0
    week_4_alarms = 0
    
    for alarm in alarm_events:
        days_ago = (today - alarm.timestamp.date()).days
        if days_ago < 7:
            week_1_alarms += 1
        elif days_ago < 14:
            week_2_alarms += 1
        elif days_ago < 21:
            week_3_alarms += 1
        elif days_ago < 28:
            week_4_alarms += 1
    
    # ============================================
    # PERFORMANCE TRENDS AND KPIs
    # ============================================
    
    # MTTR (Mean Time To Resolve) - Average time from alarm to door closure
    mttr = sum(mttr_durations) / len(mttr_durations) if mttr_durations else 0
    
    # Compliance % - Percentage of door events within allowed duration
    total_compliance_events = compliant_events + non_compliant_events
    compliance_percentage = (compliant_events / total_compliance_events * 100) if total_compliance_events > 0 else 100
    
    # Alarm reduction trend - Compare current week to previous weeks
    alarm_reduction_data = {
        'week_1': week_1_alarms,  # Current week
        'week_2': week_2_alarms,  # Last week
        'week_3': week_3_alarms,  # 2 weeks ago
        'week_4': week_4_alarms   # 3 weeks ago
    }
    
    # Calculate trend percentage (current vs previous week)
    if week_2_alarms > 0:
        alarm_reduction_percent = ((week_2_alarms - week_1_alarms) / week_2_alarms * 100)
    else:
        alarm_reduction_percent = 0 if week_1_alarms == 0 else -100
    
    # Response time trend (group by day)
    daily_response_times = {}
    for rt in response_times:
        day = rt['timestamp'].date()
        if day not in daily_response_times:
            daily_response_times[day] = []
        daily_response_times[day].append(rt['response_time'])
    
    # Calculate average response time per day
    response_time_trend = []
    for day in sorted(daily_response_times.keys()):
        avg_rt = sum(daily_response_times[day]) / len(daily_response_times[day])
        response_time_trend.append({
            'date': day.strftime('%Y-%m-%d'),
            'avg_response_time': avg_rt
        })
    
    return render_template('analytics.html',
        # Door Usage Analytics
        door_open_count_day=door_open_count_day,
        door_open_count_week=door_open_count_week,
        door_open_count_month=door_open_count_month,
        avg_open_duration=avg_open_duration,
        max_open_duration=max_open_duration,
        duration_buckets=duration_buckets,
        open_percentage=round(open_percentage, 2),
        closed_percentage=round(closed_percentage, 2),
        daily_opens=daily_opens,
        
        # Alarm Event Analysis
        total_alarms=total_alarms,
        avg_alarm_duration=avg_alarm_duration,
        longest_alarm_duration=longest_alarm_duration,
        unacknowledged_alarms=unacknowledged_alarms,
        response_time_trend=response_time_trend,
        daily_alarms=daily_alarms,
        
        # Performance Trends and KPIs
        mttr=mttr,
        compliance_percentage=round(compliance_percentage, 2),
        alarm_reduction_data=alarm_reduction_data,
        alarm_reduction_percent=round(alarm_reduction_percent, 2),
        alarm_threshold=alarm_threshold,
        
        # Common
        time_range=time_range,
        permissions=current_user.permissions.split(',')
    )

@app.route('/analytics-advanced')
@login_required
def analytics_advanced():
    """Insights page with anomaly detection and scheduled reports management"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('analytics'))
    
    return render_template('analytics_advanced.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/blockchain')
@login_required
def blockchain():
    """Blockchain audit trail verification page"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('blockchain.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/blockchain-demo')
@login_required
def blockchain_demo():
    """Customer-facing blockchain demonstration page"""
    return render_template('blockchain_demo.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/electronic-signatures')
@login_required
def electronic_signatures():
    """Electronic signatures demo page - 21 CFR Part 11"""
    return render_template('electronic_signatures.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/hipaa-compliance')
@login_required
def hipaa_compliance():
    """HIPAA compliance documentation page"""
    from datetime import datetime
    from blockchain_helper import verify_blockchain
    from models import BlockchainEventLog
    
    # Get blockchain stats
    stats = db.session.query(
        func.count(BlockchainEventLog.id).label('total_blocks'),
        func.min(BlockchainEventLog.timestamp).label('genesis_date')
    ).first()
    
    # Verify blockchain
    is_verified, verification_msg, corrupted_blocks = verify_blockchain()
    
    return render_template('hipaa_compliance.html',
        permissions=current_user.permissions.split(','),
        current_date=datetime.now().strftime('%B %d, %Y %I:%M %p'),
        total_blocks=stats.total_blocks if stats else 0,
        genesis_date=stats.genesis_date.strftime('%B %d, %Y %I:%M %p') if stats and stats.genesis_date else 'N/A',
        verification_status='✅ Verified - All blocks intact' if is_verified else '⚠ Verification needed'
    )

@app.route('/reports')
@login_required
def reports():
    if 'report' not in current_user.permissions.split(','):
        return redirect(url_for('dashboard'))
    
    # Load user preferences for date format
    from models import UserPreference
    user_pref = UserPreference.query.filter_by(user_id=current_user.id).first()
    date_format = user_pref.date_format if user_pref and user_pref.date_format else 'YYYY-MM-DD'
    
    return render_template('reports.html',
        permissions=current_user.permissions.split(','),
        user_date_format=date_format
    )

@app.route('/api/analytics/data')
@login_required
def get_analytics_data():
    """
    Returns analytics data in JSON format for AJAX real-time updates
    This allows the frontend to update metrics without page reload
    """
    if 'analytics' not in current_user.permissions.split(','):
        return jsonify({'error': 'Unauthorized'}), 403
    
    from sqlalchemy import func, and_
    
    # Get time range from request
    time_range = request.args.get('range', 'month')
    
    today = date.today()
    if time_range == 'day':
        start_date = today
    elif time_range == 'week':
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today - timedelta(days=30)
    
    # Door events
    door_events = EventLog.query.filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type.in_(['door_open', 'door_close'])
        )
    ).order_by(EventLog.timestamp.asc()).all()
    
    # Calculate door metrics
    door_open_count_day = 0
    door_open_count_week = 0
    door_open_count_month = 0
    
    for event in door_events:
        if event.event_type == 'door_open':
            event_date = event.timestamp.date()
            if event_date == today:
                door_open_count_day += 1
            if event_date >= today - timedelta(days=7):
                door_open_count_week += 1
            if event_date >= today - timedelta(days=30):
                door_open_count_month += 1
    
    # Alarm events
    alarm_events = EventLog.query.filter(
        and_(
            EventLog.timestamp >= start_date,
            EventLog.event_type == 'alarm_triggered'
        )
    ).order_by(EventLog.timestamp.asc()).all()
    
    total_alarms = len(alarm_events)
    
    # Get timer threshold
    timer_setting = Setting.query.filter_by(key='timer_duration').first()
    alarm_threshold = int(timer_setting.value) if timer_setting else 30
    
    # Calculate alarm metrics
    alarm_durations = []
    unacknowledged_alarms = 0
    
    for alarm_event in alarm_events:
        alarm_time = alarm_event.timestamp
        next_close = EventLog.query.filter(
            and_(
                EventLog.timestamp > alarm_time,
                EventLog.event_type == 'door_close'
            )
        ).order_by(EventLog.timestamp.asc()).first()
        
        if next_close:
            alarm_duration = (next_close.timestamp - alarm_time).total_seconds()
            alarm_durations.append(alarm_duration)
            
            if alarm_duration > (alarm_threshold * 2):
                unacknowledged_alarms += 1
        else:
            unacknowledged_alarms += 1
    
    avg_alarm_duration = sum(alarm_durations) / len(alarm_durations) if alarm_durations else 0
    longest_alarm_duration = max(alarm_durations) if alarm_durations else 0
    
    # MTTR
    mttr = avg_alarm_duration
    
    # Compliance
    compliant = sum(1 for d in alarm_durations if d <= (alarm_threshold * 2))
    total_compliance = len(alarm_durations) + unacknowledged_alarms
    compliance_percentage = (compliant / total_compliance * 100) if total_compliance > 0 else 100
    
    # Weekly alarm counts for reduction trend
    week_1_alarms = 0
    week_2_alarms = 0
    week_3_alarms = 0
    week_4_alarms = 0
    
    for alarm in alarm_events:
        days_ago = (today - alarm.timestamp.date()).days
        if days_ago < 7:
            week_1_alarms += 1
        elif days_ago < 14:
            week_2_alarms += 1
        elif days_ago < 21:
            week_3_alarms += 1
        elif days_ago < 28:
            week_4_alarms += 1
    
    # Alarm reduction percentage
    if week_2_alarms > 0:
        alarm_reduction_percent = ((week_2_alarms - week_1_alarms) / week_2_alarms * 100)
    else:
        alarm_reduction_percent = 0 if week_1_alarms == 0 else -100
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'time_range': time_range,
        'door_metrics': {
            'door_open_count_day': door_open_count_day,
            'door_open_count_week': door_open_count_week,
            'door_open_count_month': door_open_count_month
        },
        'alarm_metrics': {
            'total_alarms': total_alarms,
            'avg_alarm_duration': round(avg_alarm_duration, 1),
            'longest_alarm_duration': round(longest_alarm_duration, 1),
            'unacknowledged_alarms': unacknowledged_alarms
        },
        'performance_metrics': {
            'mttr': round(mttr, 1),
            'compliance_percentage': round(compliance_percentage, 2),
            'alarm_reduction_percent': round(alarm_reduction_percent, 2),
            'alarm_threshold': alarm_threshold,
            'weekly_alarms': {
                'week_1': week_1_alarms,
                'week_2': week_2_alarms,
                'week_3': week_3_alarms,
                'week_4': week_4_alarms
            }
        }
    })

@app.route('/api/events')
@login_required
def get_events():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    since_id = request.args.get('since', 0, type=int)  # For polling - get events since this ID
    
    # If 'since' parameter is provided, return new events for polling
    if since_id > 0:
        print(f"[API] Polling request: Getting events since ID {since_id}")
        new_events = EventLog.query.filter(EventLog.id > since_id).order_by(EventLog.timestamp.desc()).limit(per_page).all()
        print(f"[API] Found {len(new_events)} new events since ID {since_id}")
        return jsonify({
            'events': [event.to_dict() for event in new_events],
            'total': len(new_events),
            'since_id': since_id,
            'latest_id': new_events[0].id if new_events else since_id,
            'polling': True
        })
    
    # Regular paginated request
    events = EventLog.query.order_by(EventLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return jsonify({
        'events': [event.to_dict() for event in events.items],
        'total': events.total,
        'pages': events.pages,
        'current_page': page,
        'polling': False
    })

@app.route('/api/events/<int:event_id>')
@login_required
def get_single_event(event_id):
    """Get a single event by ID with updated image data"""
    event = EventLog.query.get_or_404(event_id)
    return jsonify(event.to_dict())

@app.route('/api/statistics')
@login_required
def get_statistics():
    """Get real-time event statistics"""
    total_events = EventLog.query.count()
    door_open_events = EventLog.query.filter_by(event_type='door_open').count()
    door_close_events = EventLog.query.filter_by(event_type='door_close').count()
    alarm_events = EventLog.query.filter_by(event_type='alarm_triggered').count()
    
    return jsonify({
        'total_events': total_events,
        'door_open_events': door_open_events,
        'door_close_events': door_close_events,
        'alarm_events': alarm_events
    })

@app.route('/api/settings', methods=['POST'])
@login_required
def update_settings():
    if 'controls' not in current_user.permissions.split(','):
        return jsonify({'error': 'Permission denied'}), 403
        
    data = request.get_json()
    if 'timer_duration' in data:
        setting = Setting.query.filter_by(key='timer_duration').first()
        if setting:
            setting.value = str(data['timer_duration'])
            db.session.commit()
            log_event('setting_changed', f'Timer duration changed to {data["timer_duration"]} seconds')
            return jsonify({'success': True})
    return jsonify({'error': 'Invalid setting'}), 400

@app.route('/api/backup')
@login_required
def backup_database():
    if 'controls' not in current_user.permissions.split(','):
        return jsonify({'error': 'Permission denied'}), 403
        
    return send_file('instance/alarm_system.db', as_attachment=True, download_name='alarm_system_backup.db')

@app.route('/api/test-event', methods=['POST'])
@login_required
def test_event():
    """Test endpoint to simulate door events for testing auto-refresh"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
        
    try:
        data = request.get_json()
        event_type = data.get('event_type', 'door_open')
        description = data.get('description', f'Test {event_type} event')
        
        # Valid event types
        valid_types = ['door_open', 'door_close', 'alarm_triggered', 'test_event']
        if event_type not in valid_types:
            return jsonify({'error': 'Invalid event type'}), 400
            
        # Log the test event
        print(f"[TEST] Manually triggering test event: {event_type}")
        log_event(event_type, description)
        
        return jsonify({
            'success': True,
            'message': f'Test event "{event_type}" created successfully',
            'event_type': event_type,
            'description': description
        })
        
    except Exception as e:
        print(f"[ERROR] Test event failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['POST'])
@login_required
def generate_report():
    if 'report' not in current_user.permissions.split(','):
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        # Import models at the beginning
        from models import CompanyProfile, DoorSystemInfo, UserPreference
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d') + timedelta(days=1)
        event_types = data.get('event_types', [])
        
        query = EventLog.query.filter(EventLog.timestamp.between(start_date, end_date))
        if event_types:
            query = query.filter(EventLog.event_type.in_(event_types))
            
        events = query.all()
        
        # Get company and system info (used by all export formats)
        company_profile = CompanyProfile.query.first()
        door_system_info = DoorSystemInfo.query.first()
        
        # Load user preferences for date/time formatting
        user_pref = UserPreference.query.filter_by(user_id=current_user.id).first()
        date_format = user_pref.date_format if user_pref and user_pref.date_format else 'YYYY-MM-DD'
        time_format = user_pref.time_format if user_pref and user_pref.time_format else '24h'
        
        # Create format mapping for Python strftime
        date_format_map = {
            'YYYY-MM-DD': '%Y-%m-%d',
            'DD/MM/YYYY': '%d/%m/%Y',
            'MM/DD/YYYY': '%m/%d/%Y',
            'DD-MM-YYYY': '%d-%m-%Y'
        }
        time_format_map = {
            '24h': '%H:%M:%S',
            '12h': '%I:%M:%S %p'
        }
        
        date_fmt = date_format_map.get(date_format, '%Y-%m-%d')
        time_fmt = time_format_map.get(time_format, '%H:%M:%S')
        datetime_fmt = f"{date_fmt} {time_fmt}"
        
        # For CSV
        if data.get('format') == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Add metadata header
            writer.writerow(['# eDOMOS Security Report - CSV Export'])
            writer.writerow([f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([f'# Generated By: {current_user.full_name if current_user.full_name else current_user.username}'])
            
            if company_profile and company_profile.company_name:
                writer.writerow([f'# Company: {company_profile.company_name}'])
            
            if door_system_info:
                if door_system_info.door_location:
                    writer.writerow([f'# Door Location: {door_system_info.door_location}'])
                if door_system_info.device_serial_number:
                    writer.writerow([f'# Device S/N: {door_system_info.device_serial_number}'])
            
            writer.writerow([f'# Report Period: {data.get("start_date")} to {data.get("end_date")}'])
            writer.writerow(['#'])
            
            # Data header with additional fields
            headers = ['ID', 'Event Type', 'Description', 'Timestamp']
            if current_user.employee_id:
                headers.append('Logged By ID')
            if door_system_info and door_system_info.door_location:
                headers.append('Location')
            
            writer.writerow(headers)
            
            # Event data
            for event in events:
                # Format timestamp using user preference
                formatted_timestamp = event.timestamp.strftime(datetime_fmt)
                row = [event.id, event.event_type, event.description, formatted_timestamp]
                if current_user.employee_id:
                    row.append(current_user.employee_id)
                if door_system_info and door_system_info.door_location:
                    row.append(door_system_info.door_location)
                writer.writerow(row)
                
            output.seek(0)
            return jsonify({'csv_data': output.getvalue()})
        
        # For PDF - INDUSTRIAL-GRADE AUDIT-READY DESIGN
        elif data.get('format') == 'pdf':
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch, mm
                from reportlab.lib import colors
                from reportlab.platypus.flowables import HRFlowable
                from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
                from reportlab.pdfgen import canvas
                from io import BytesIO
                import base64
            except ImportError as e:
                return jsonify({'error': f'PDF generation libraries not available: {str(e)}'}), 500
            
            # ==================== PROFESSIONAL HEADER/FOOTER TEMPLATE ====================
            class AuditReportTemplate(SimpleDocTemplate):
                def __init__(self, *args, **kwargs):
                    self.report_data = kwargs.pop('report_data', {})
                    self.company_profile = kwargs.pop('company_profile', None)
                    self.door_system_info = kwargs.pop('door_system_info', None)
                    SimpleDocTemplate.__init__(self, *args, **kwargs)
                
                def afterPage(self):
                    """Add header and footer to each page"""
                    self.handle_pageBegin()
                    canvas_obj = self.canv
                    
                    # Define colors
                    primary_blue = colors.HexColor('#0066CC')
                    dark_gray = colors.HexColor('#1A1A1A')
                    medium_gray = colors.HexColor('#555555')
                    light_gray = colors.HexColor('#CCCCCC')
                    
                    # PAGE HEADER (top of every page)
                    canvas_obj.saveState()
                    
                    # Top border - Bold blue line
                    canvas_obj.setStrokeColor(primary_blue)
                    canvas_obj.setLineWidth(3)
                    canvas_obj.line(self.leftMargin, A4[1] - 0.6*inch, A4[0] - self.rightMargin, A4[1] - 0.6*inch)
                    
                    # Company/System name (top left)
                    canvas_obj.setFont('Helvetica-Bold', 9)
                    canvas_obj.setFillColor(dark_gray)
                    canvas_obj.drawString(self.leftMargin, A4[1] - 0.5*inch, "eDOMOS SECURITY SYSTEM")
                    
                    # Document ID and Classification (top right)
                    canvas_obj.setFont('Helvetica', 7)
                    canvas_obj.setFillColor(medium_gray)
                    doc_id = f"DOC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    canvas_obj.drawRightString(A4[0] - self.rightMargin, A4[1] - 0.45*inch, f"Document ID: {doc_id}")
                    canvas_obj.drawRightString(A4[0] - self.rightMargin, A4[1] - 0.55*inch, "Classification: CONFIDENTIAL")
                    
                    # PAGE FOOTER (bottom of every page)
                    
                    # Bottom border - Thin gray line
                    canvas_obj.setStrokeColor(light_gray)
                    canvas_obj.setLineWidth(0.5)
                    canvas_obj.line(self.leftMargin, 0.75*inch, A4[0] - self.rightMargin, 0.75*inch)
                    
                    # Footer left: System info and company name
                    canvas_obj.setFont('Helvetica', 7)
                    canvas_obj.setFillColor(medium_gray)
                    
                    # Show company name if available
                    footer_line1 = "eDOMOS Door Monitoring System"
                    if self.company_profile and self.company_profile.company_name:
                        footer_line1 = self.company_profile.company_name
                    
                    footer_line2 = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    if self.door_system_info and self.door_system_info.door_location:
                        footer_line2 = f"{self.door_system_info.door_location} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    canvas_obj.drawString(self.leftMargin, 0.6*inch, footer_line1)
                    canvas_obj.drawString(self.leftMargin, 0.5*inch, footer_line2)
                    
                    # Footer center: Security notice
                    canvas_obj.setFont('Helvetica-Oblique', 7)
                    canvas_obj.drawCentredString(A4[0]/2, 0.6*inch, "SECURITY AUDIT REPORT")
                    canvas_obj.drawCentredString(A4[0]/2, 0.5*inch, "This document contains confidential information")
                    
                    # Footer right: Page number
                    canvas_obj.setFont('Helvetica-Bold', 8)
                    canvas_obj.setFillColor(dark_gray)
                    page_text = f"Page {canvas_obj.getPageNumber()}"
                    canvas_obj.drawRightString(A4[0] - self.rightMargin, 0.55*inch, page_text)
                    
                    canvas_obj.restoreState()
            
            buffer = BytesIO()
            
            # Page Setup: A4, Portrait, optimized margins for printing
            doc = AuditReportTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=1*inch,
                title=f"eDOMOS Security Audit Report - {data.get('start_date')} to {data.get('end_date')}",
                author="eDOMOS Security System",
                subject="Door Monitoring Security Audit Report",
                report_data={'start_date': data.get('start_date'), 'end_date': data.get('end_date')},
                company_profile=company_profile,
                door_system_info=door_system_info
            )
            
            # ==================== PROFESSIONAL COLOR PALETTE ====================
            # Primary colors
            primary_blue = colors.HexColor('#0066CC')
            accent_teal = colors.HexColor('#00897B')
            
            # Text colors
            dark_text = colors.HexColor('#1A1A1A')
            medium_text = colors.HexColor('#424242')
            light_text = colors.HexColor('#757575')
            
            # Background colors
            header_bg = colors.HexColor('#E3F2FD')       # Light blue
            header_accent = colors.HexColor('#BBDEFB')   # Darker blue
            alt_row_bg = colors.HexColor('#F5F5F5')      # Light gray
            highlight_bg = colors.HexColor('#FFF9C4')    # Light yellow for alerts
            
            # Status colors
            status_success = colors.HexColor('#4CAF50')  # Green
            status_warning = colors.HexColor('#FF9800')  # Orange
            status_error = colors.HexColor('#F44336')    # Red
            status_info = colors.HexColor('#2196F3')     # Blue
            
            # ==================== TYPOGRAPHY STYLES ====================
            styles = getSampleStyleSheet()
            
            # Main Title - Bold, Large, Professional
            main_title_style = ParagraphStyle(
                'MainTitle',
                parent=styles['Title'],
                fontSize=24,
                fontName='Helvetica-Bold',
                textColor=primary_blue,
                spaceAfter=6,
                spaceBefore=8,
                alignment=TA_CENTER,
                leading=28
            )
            
            # Subtitle - Document Type
            doc_subtitle_style = ParagraphStyle(
                'DocSubtitle',
                parent=styles['Normal'],
                fontSize=14,
                fontName='Helvetica',
                textColor=medium_text,
                spaceAfter=20,
                alignment=TA_CENTER,
                leading=18
            )
            
            # Section Header - For major sections
            section_header_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading1'],
                fontSize=14,
                fontName='Helvetica-Bold',
                textColor=dark_text,
                spaceAfter=12,
                spaceBefore=20,
                alignment=TA_LEFT,
                borderWidth=0,
                borderColor=primary_blue,
                borderPadding=0,
                leftIndent=0,
                leading=18
            )
            
            # Stats Label (for summary boxes)
            stats_label_style = ParagraphStyle(
                'StatsLabel',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                textColor=light_text,
                spaceAfter=2,
                alignment=TA_LEFT,
                leading=12
            )
            
            # Stats Value (for summary boxes)
            stats_value_style = ParagraphStyle(
                'StatsValue',
                parent=styles['Normal'],
                fontSize=16,
                fontName='Helvetica-Bold',
                textColor=primary_blue,
                spaceAfter=4,
                alignment=TA_LEFT,
                leading=20
            )
            
            # Info Label (key-value pairs)
            info_label_style = ParagraphStyle(
                'InfoLabel',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold',
                textColor=dark_text,
                spaceAfter=0,
                leading=14
            )
            
            # Info Value (key-value pairs)
            info_value_style = ParagraphStyle(
                'InfoValue',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica',
                textColor=medium_text,
                spaceAfter=0,
                leading=14
            )
            
            # Table cell style
            table_cell_style = ParagraphStyle(
                'TableCell',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                textColor=dark_text,
                alignment=TA_LEFT,
                leading=12
            )
            
            # Table header style
            table_header_style = ParagraphStyle(
                'TableHeader',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=dark_text,
                alignment=TA_CENTER,
                leading=12
            )
            
            # ==================== BUILD PDF CONTENT ====================
            story = []
            
            # Company profile and door system info already loaded above
            
            # ==================== TITLE PAGE SECTION ====================
            story.append(Spacer(1, 0.2*inch))
            
            # Company Logo (if available)
            if company_profile and company_profile.logo_path:
                try:
                    from reportlab.platypus import Image
                    logo_path = os.path.join(app.root_path, 'static', company_profile.logo_path.lstrip('/static/'))
                    if os.path.exists(logo_path):
                        logo = Image(logo_path, width=1.5*inch, height=1.5*inch, kind='proportional')
                        logo.hAlign = 'CENTER'
                        story.append(logo)
                        story.append(Spacer(1, 0.15*inch))
                except Exception as e:
                    print(f"[WARNING] Could not add logo to PDF: {e}")
            
            # Company Name (if available)
            if company_profile and company_profile.company_name:
                company_name_style = ParagraphStyle(
                    'CompanyName',
                    parent=styles['Normal'],
                    fontSize=11,
                    fontName='Helvetica-Bold',
                    textColor=dark_text,
                    alignment=TA_CENTER,
                    spaceAfter=10
                )
                story.append(Paragraph(company_profile.company_name, company_name_style))
            
            # Main Title
            story.append(Paragraph("DOOR MONITORING", main_title_style))
            story.append(Paragraph("SECURITY AUDIT REPORT", main_title_style))
            story.append(Spacer(1, 0.15*inch))
            
            # Document type badge with door location
            doc_subtitle_text = "Access Control & Event Log"
            if door_system_info and door_system_info.door_location:
                doc_subtitle_text += f" - {door_system_info.door_location}"
            story.append(Paragraph(doc_subtitle_text, doc_subtitle_style))
            
            # Decorative separator
            story.append(HRFlowable(
                width="40%",
                thickness=2,
                color=primary_blue,
                spaceAfter=30,
                spaceBefore=10
            ))
            
            # ==================== EXECUTIVE SUMMARY SECTION ====================
            story.append(Paragraph("EXECUTIVE SUMMARY", section_header_style))
            
            # Calculate comprehensive statistics
            door_open_count = sum(1 for e in events if e.event_type == 'door_open')
            door_close_count = sum(1 for e in events if e.event_type == 'door_close')
            alarm_count = sum(1 for e in events if e.event_type == 'alarm_triggered')
            timer_set_count = sum(1 for e in events if e.event_type == 'timer_set')
            
            # Create statistics cards (4 columns) - Fixed overlapping issue
            # Build each card as a mini-table to ensure proper layout
            cards = []
            stats_info = [
                ("TOTAL EVENTS", str(len(events)), '#0066CC'),
                ("DOOR OPENS", str(door_open_count), '#FF9800'),
                ("DOOR CLOSES", str(door_close_count), '#4CAF50'),
                ("ALARMS", str(alarm_count), '#F44336'),
            ]
            
            for label, value, color in stats_info:
                card_data = [
                    [Paragraph(f"<para align='center'><font size='9' color='#757575'><b>{label}</b></font></para>", styles['Normal'])],
                    [Paragraph(f"<para align='center'><font size='20' color='{color}'><b>{value}</b></font></para>", styles['Normal'])],
                ]
                card_table = Table(card_data, colWidths=[1.75*inch])
                card_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
                    ('TOPPADDING', (0, 1), (-1, 1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ]))
                cards.append(card_table)
            
            stats_table = Table([cards], colWidths=[1.85*inch, 1.85*inch, 1.85*inch, 1.85*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), header_bg),
                ('BOX', (0, 0), (-1, -1), 1.5, primary_blue),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROUNDEDCORNERS', [8, 8, 8, 8]),  # Rounded corners: [topLeft, topRight, bottomLeft, bottomRight]
            ]))
            
            story.append(stats_table)
            story.append(Spacer(1, 0.25*inch))
            
            # ==================== REPORT INFORMATION SECTION ====================
            story.append(Paragraph("REPORT INFORMATION", section_header_style))
            
            # Prepare report metadata
            date_range = f"{data.get('start_date', 'N/A')} to {data.get('end_date', 'N/A')}"
            event_filter = ', '.join([t.replace('_', ' ').title() for t in event_types]) if event_types else 'All Event Types'
            generated_date = datetime.now().strftime('%B %d, %Y')
            generated_time = datetime.now().strftime('%I:%M:%S %p')
            
            # Get user info for "Generated by" field
            generated_by = current_user.full_name if current_user.full_name else current_user.username
            if current_user.employee_id:
                generated_by += f" (ID: {current_user.employee_id})"
            if current_user.department:
                generated_by += f" - {current_user.department}"
            
            # Build door location info
            door_location_info = "eDOMOS v2.1 - Door Monitoring System"
            if door_system_info:
                if door_system_info.door_location:
                    door_location_info = f"{door_system_info.door_location}"
                    if door_system_info.department_name:
                        door_location_info += f" ({door_system_info.department_name})"
                if door_system_info.device_serial_number:
                    door_location_info += f" - S/N: {door_system_info.device_serial_number}"
            
            # Create modern 2-column metadata table with gradient effect
            info_data = [
                [Paragraph("<b>Report Period:</b>", info_label_style), Paragraph(date_range, info_value_style)],
                [Paragraph("<b>Event Filter:</b>", info_label_style), Paragraph(event_filter, info_value_style)],
                [Paragraph("<b>Total Records:</b>", info_label_style), Paragraph(f"{len(events)} events recorded", info_value_style)],
                [Paragraph("<b>Door Location:</b>", info_label_style), Paragraph(door_location_info, info_value_style)],
                [Paragraph("<b>Report Generated:</b>", info_label_style), Paragraph(f"{generated_date} at {generated_time}", info_value_style)],
                [Paragraph("<b>Generated By:</b>", info_label_style), Paragraph(generated_by, info_value_style)],
                [Paragraph("<b>Report Type:</b>", info_label_style), Paragraph("Security Audit - Access Control Log", info_value_style)],
            ]
            
            # Add company info if available
            if company_profile and company_profile.company_name:
                company_info = company_profile.company_name
                if company_profile.company_city and company_profile.company_state:
                    company_info += f" - {company_profile.company_city}, {company_profile.company_state}"
                info_data.insert(3, [Paragraph("<b>Facility:</b>", info_label_style), Paragraph(company_info, info_value_style)])
            
            info_table = Table(info_data, colWidths=[2*inch, 5.4*inch])
            info_table.setStyle(TableStyle([
                # Modern look with subtle gradients using alternating backgrounds
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8EAF6')),  # Light indigo for labels
                ('BACKGROUND', (1, 0), (1, -1), colors.white),  # White for values
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), dark_text),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                # Outer border with primary color
                ('BOX', (0, 0), (-1, -1), 1.5, primary_blue),
                # Horizontal lines between rows for clarity
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#E0E0E0')),
                ('ROUNDEDCORNERS', [8, 8, 8, 8]),  # Rounded corners
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 0.3*inch))
            
            # ==================== EVENT LOG TABLE SECTION ====================
            story.append(Paragraph("DETAILED EVENT LOG", section_header_style))
            story.append(Spacer(1, 0.1*inch))
            
            if events:
                # Build table with enhanced styling
                table_data = [[
                    Paragraph('<b>ID</b>', table_header_style),
                    Paragraph('<b>DATE & TIME</b>', table_header_style),
                    Paragraph('<b>EVENT TYPE</b>', table_header_style),
                    Paragraph('<b>STATUS</b>', table_header_style),
                    Paragraph('<b>USER/SOURCE</b>', table_header_style)
                ]]
                
                # Populate table rows
                for idx, event in enumerate(events):
                    event_id = f"#{event.id}"
                    
                    # Format timestamp using user preference with line break
                    date_time = event.timestamp.strftime(date_fmt) + '<br/>' + event.timestamp.strftime(time_fmt)
                    
                    # Format event type
                    event_type_display = event.event_type.replace('_', ' ').title()
                    
                    # Determine status with colored indicator
                    if event.event_type == 'door_open':
                        status = '<font color="#FF9800">●</font> OPEN'
                        row_bg = colors.white if idx % 2 == 0 else alt_row_bg
                    elif event.event_type == 'door_close':
                        status = '<font color="#4CAF50">●</font> CLOSED'
                        row_bg = colors.white if idx % 2 == 0 else alt_row_bg
                    elif event.event_type == 'alarm_triggered':
                        status = '<font color="#F44336">●</font> ALERT'
                        row_bg = highlight_bg  # Highlight alarms
                    elif event.event_type == 'timer_set':
                        status = '<font color="#2196F3">●</font> TIMER'
                        row_bg = colors.white if idx % 2 == 0 else alt_row_bg
                    else:
                        status = '<font color="#9E9E9E">●</font> INFO'
                        row_bg = colors.white if idx % 2 == 0 else alt_row_bg
                    
                    user_name = "SYSTEM"
                    
                    table_data.append([
                        Paragraph(f'<para align="center"><b>{event_id}</b></para>', table_cell_style),
                        Paragraph(f'<para align="center">{date_time}</para>', table_cell_style),
                        Paragraph(event_type_display, table_cell_style),
                        Paragraph(f'<para align="center"><b>{status}</b></para>', table_cell_style),
                        Paragraph(user_name, table_cell_style)
                    ])
                
                # Create table with optimized column widths
                event_table = Table(
                    table_data,
                    colWidths=[0.65*inch, 1.4*inch, 2*inch, 1.35*inch, 1.4*inch],
                    repeatRows=1  # Header repeats on each page
                )
                
                # Apply modern, professional table styling with gradients
                table_style_list = [
                    # Modern Header with gradient effect (dark to light blue)
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('TOPPADDING', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                    
                    # Data rows - general styling
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('TOPPADDING', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Modern borders - clean outer box with subtle inner lines
                    ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1976D2')),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0D47A1')),
                    ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.HexColor('#E0E0E0')),
                    ('ROUNDEDCORNERS', [8, 8, 8, 8]),  # Rounded corners
                ]
                
                # Apply modern alternating row colors with subtle gradient effect
                for i in range(1, len(table_data)):
                    event_type = events[i-1].event_type
                    if event_type == 'alarm_triggered':
                        # Highlight alarms with soft red/pink
                        table_style_list.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFEBEE')))
                        table_style_list.append(('LEFTPADDING', (0, i), (0, i), 10))
                    elif i % 2 == 0:
                        # Alternating very light blue-gray
                        table_style_list.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F5F7FA')))
                    else:
                        # White background
                        table_style_list.append(('BACKGROUND', (0, i), (-1, i), colors.white))
                
                event_table.setStyle(TableStyle(table_style_list))
                story.append(event_table)
            else:
                # No events found message
                no_data_para = Paragraph(
                    "<para align='center' backColor='#FFF3E0' borderColor='#FF9800' borderWidth='1' "
                    "borderPadding='20'><b>NO EVENTS FOUND</b><br/>"
                    "No events match the specified criteria for the selected time period.</para>",
                    doc_subtitle_style
                )
                story.append(no_data_para)
            
            # ==================== COMPLIANCE & AUDIT SECTION ====================
            # Add compliance metrics for ISO 27001 / SOC 2 audits
            if data.get('report_type') == 'compliance_audit':
                story.append(Spacer(1, 0.3*inch))
                story.append(Paragraph("COMPLIANCE & AUDIT METRICS", section_header_style))
                story.append(Spacer(1, 0.1*inch))
                
                # Calculate compliance metrics
                alarm_events_list = [e for e in events if e.event_type == 'alarm_triggered']
                total_alarms = len(alarm_events_list)
                
                # Get anomalies in the same period
                anomalies = AnomalyDetection.query.filter(
                    AnomalyDetection.detected_at.between(start_date, end_date)
                ).all()
                total_anomalies = len(anomalies)
                unacknowledged_anomalies = len([a for a in anomalies if not a.is_acknowledged])
                
                # Compliance percentage (from analytics)
                timer_setting = Setting.query.filter_by(key='timer_duration').first()
                alarm_threshold = int(timer_setting.value) if timer_setting else 30
                
                # Calculate MTTR (Mean Time To Resolve)
                mttr_durations = []
                for alarm in alarm_events_list:
                    # Find the next door_close event after this alarm
                    close_event = EventLog.query.filter(
                        EventLog.event_type == 'door_close',
                        EventLog.timestamp > alarm.timestamp
                    ).order_by(EventLog.timestamp.asc()).first()
                    
                    if close_event:
                        duration = (close_event.timestamp - alarm.timestamp).total_seconds()
                        mttr_durations.append(duration)
                
                mttr = sum(mttr_durations) / len(mttr_durations) if mttr_durations else 0
                
                # Build compliance table
                compliance_data = [
                    [Paragraph("<b>Metric</b>", info_label_style), Paragraph("<b>Value</b>", info_label_style), Paragraph("<b>Standard</b>", info_label_style)],
                    [Paragraph("Total Security Events", info_value_style), Paragraph(str(len(events)), info_value_style), Paragraph("ISO 27001:2013", info_value_style)],
                    [Paragraph("Alarm Events Triggered", info_value_style), Paragraph(str(total_alarms), info_value_style), Paragraph("Access Control (A.9.1)", info_value_style)],
                    [Paragraph("Anomalies Detected", info_value_style), Paragraph(str(total_anomalies), info_value_style), Paragraph("Monitoring (A.12.4)", info_value_style)],
                    [Paragraph("Unacknowledged Anomalies", info_value_style), Paragraph(str(unacknowledged_anomalies), info_value_style), Paragraph("Incident Response", info_value_style)],
                    [Paragraph("Mean Time To Resolve (MTTR)", info_value_style), Paragraph(f"{mttr:.1f} seconds", info_value_style), Paragraph("SOC 2 CC7.3", info_value_style)],
                    [Paragraph("Alarm Threshold Setting", info_value_style), Paragraph(f"{alarm_threshold} seconds", info_value_style), Paragraph("Policy Compliance", info_value_style)],
                ]
                
                compliance_table = Table(compliance_data, colWidths=[2.5*inch, 2*inch, 2*inch])
                compliance_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), header_bg),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(compliance_table)
                story.append(Spacer(1, 0.2*inch))
            
            # ==================== CERTIFICATION & SIGNATURES SECTION ====================
            # Create signature section elements
            signature_elements = []
            
            signature_elements.append(Spacer(1, 0.3*inch))
            signature_elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC')))
            signature_elements.append(Spacer(1, 0.15*inch))
            
            # Certification statement
            cert_style = ParagraphStyle(
                'Certification',
                parent=styles['Normal'],
                fontSize=8,
                fontName='Helvetica-Oblique',
                textColor=light_text,
                alignment=TA_JUSTIFY,
                leading=11
            )
            
            # Build certification text based on report type
            if data.get('report_type') == 'compliance_audit':
                certification_text = (
                    "<b>CERTIFICATION & COMPLIANCE STATEMENT:</b> This report was automatically generated by the eDOMOS Door Monitoring System "
                    "in compliance with ISO/IEC 27001:2013 information security standards and SOC 2 Trust Service Criteria. "
                    "All timestamps are recorded in local system time with audit trail preservation. Event data is stored in a secure database "
                    "with integrity controls and access restrictions. This document contains sensitive security information and is intended for "
                    "authorized personnel, auditors, and compliance officers only. The system maintains continuous monitoring for anomaly detection, "
                    "incident response tracking (MTTR), and access control verification as required by applicable security frameworks."
                )
            else:
                certification_text = (
                    "<b>CERTIFICATION:</b> This report was automatically generated by the eDOMOS Door Monitoring System. "
                    "All timestamps are recorded in local system time. Event data is stored in a secure database and "
                    "is subject to audit trails. This document is intended for authorized personnel only and contains "
                    "sensitive security information regarding access control and facility monitoring."
                )
            signature_elements.append(Paragraph(certification_text, cert_style))
            signature_elements.append(Spacer(1, 0.2*inch))
            
            # Signature blocks (for manual signatures if needed) - Aligned to certification text width
            sig_style = ParagraphStyle(
                'SignatureBlock',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_LEFT,  # Left-align text within each block
                leading=12
            )
            
            sig_data = [
                [
                    Paragraph("<b>Prepared By:</b><br/>__________________________<br/><font size='7'>System Administrator</font>", sig_style),
                    Paragraph("<b>Reviewed By:</b><br/>__________________________<br/><font size='7'>Security Officer</font>", sig_style),
                    Paragraph("<b>Date:</b><br/>__________________________<br/><font size='7'>Approval Date</font>", sig_style),
                ]
            ]
            
            # Match the width of the content area (same as certification text)
            # Page width is 8.5 inches, with 1 inch margins on each side = 6.5 inches usable width
            # Divide equally among 3 columns
            available_width = 6.5*inch
            col_width = available_width / 3
            sig_table = Table(sig_data, colWidths=[col_width, col_width, col_width])
            sig_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Prepared By - left aligned
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Reviewed By - center aligned
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),   # Date - right aligned
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),   # No left padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # No right padding
            ]))
            
            signature_elements.append(sig_table)
            
            # Wrap signature section in KeepTogether to prevent page breaks
            story.append(KeepTogether(signature_elements))
            
            # ==================== BUILD AND RETURN PDF ====================
            try:
                doc.build(story)
                buffer.seek(0)
                pdf_data = base64.b64encode(buffer.getvalue()).decode()
                return jsonify({'pdf_data': pdf_data})
            
            except Exception as e:
                print(f"PDF Generation Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
        
        # For JSON (default)
        # Company profile and door system info already loaded above
        
        # Build metadata
        metadata = {
            'report_generated': datetime.now().isoformat(),
            'generated_by': {
                'username': current_user.username,
                'full_name': current_user.full_name,
                'employee_id': current_user.employee_id,
                'department': current_user.department,
                'role': current_user.role
            },
            'report_period': {
                'start_date': data.get('start_date'),
                'end_date': data.get('end_date')
            },
            'total_events': len(events)
        }
        
        # Add company info if available
        if company_profile:
            metadata['company'] = {
                'name': company_profile.company_name,
                'address': f"{company_profile.company_address}, {company_profile.company_city}, {company_profile.company_state} {company_profile.company_zip}",
                'phone': company_profile.company_phone,
                'email': company_profile.company_email
            }
        
        # Add system info if available
        if door_system_info:
            metadata['system'] = {
                'door_location': door_system_info.door_location,
                'department': door_system_info.department_name,
                'device_serial_number': door_system_info.device_serial_number,
                'system_model': door_system_info.system_model
            }
        
        # Format events with user's preferred date/time format
        formatted_events = []
        for event in events:
            event_dict = {
                'id': event.id,
                'event_type': event.event_type,
                'description': event.description,
                'timestamp': event.timestamp.strftime(datetime_fmt)
            }
            formatted_events.append(event_dict)
        
        return jsonify({
            'metadata': metadata,
            'events': formatted_events
        })
        
    except Exception as e:
        print(f"Report Generation Error: {str(e)}")

# All test routes removed for production deployment

# Note: WebSocket events are already defined above - no duplicate handlers needed

@app.route('/api/dashboard')
@login_required
def api_dashboard():
    """Get complete dashboard data for real-time updates"""
    try:
        global door_open, alarm_active
        
        # Get system status
        door_status = "Open" if door_open else "Closed"
        alarm_status = "Active" if alarm_active else "Inactive"
        timer_setting = Setting.query.filter_by(key='timer_duration').first()
        timer_set = timer_setting.value if timer_setting else '30'
        
        # Get event counts
        total_events = EventLog.query.count()
        door_open_events = EventLog.query.filter_by(event_type='door_open').count()
        door_close_events = EventLog.query.filter_by(event_type='door_close').count()
        alarm_events = EventLog.query.filter_by(event_type='alarm_triggered').count()
        
        # Get last event
        last_event = EventLog.query.order_by(EventLog.timestamp.desc()).first()
        last_event_data = last_event.to_dict() if last_event else None
        
        # Get recent events for dashboard display
        recent_events = EventLog.query.order_by(EventLog.timestamp.desc()).limit(5).all()
        recent_events_data = [event.to_dict() for event in recent_events]
        
        # Get system uptime
        uptime_data = calculate_uptime()
        
        return jsonify({
            'door_status': door_status,
            'alarm_status': alarm_status,
            'timer_set': timer_set,
            'total_events': total_events,
            'door_open_events': door_open_events,
            'door_close_events': door_close_events,
            'alarm_events': alarm_events,
            'last_event': last_event_data,
            'recent_events': recent_events_data,
            'uptime': uptime_data,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }), 200, {'Cache-Control': 'no-cache, no-store, must-revalidate'}
    
    except Exception as e:
        print(f"[ERROR] Dashboard API error: {e}")
        return jsonify({
            'error': 'Failed to get dashboard data',
            'success': False
        }), 500

@app.route('/api/uptime')
@login_required
def api_uptime():
    """Get system uptime information"""
    try:
        uptime_data = calculate_uptime()
        return jsonify({
            'uptime': uptime_data,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }), 200, {'Cache-Control': 'no-cache, no-store, must-revalidate'}
    
    except Exception as e:
        print(f"[ERROR] Uptime API error: {e}")
        return jsonify({
            'error': 'Failed to get uptime data',
            'success': False
        }), 500

@app.route('/api/status')
@login_required
def api_status():
    """Get current system status for real-time updates"""
    try:
        global door_open, alarm_active
        
        # Get timer setting
        timer_setting = Setting.query.filter_by(key='timer_duration').first()
        timer_set = timer_setting.value if timer_setting else '30'
        
        return jsonify({
            'door_status': 'Open' if door_open else 'Closed',
            'alarm_status': 'Active' if alarm_active else 'Inactive',
            'timer_set': timer_set,
            'timestamp': datetime.now().isoformat(),
            'success': True
        }), 200, {'Cache-Control': 'no-cache, no-store, must-revalidate'}
    
    except Exception as e:
        print(f"[ERROR] Status API error: {e}")
        return jsonify({
            'error': 'Failed to get system status',
            'success': False
        }), 500

@app.route('/websocket-test')
def websocket_test():
    """WebSocket connection test page"""
    return render_template('websocket_test.html')

# ==================== COMPANY PROFILE & CUSTOMIZATION ROUTES ====================

@app.route('/company-profile')
@login_required
def company_profile():
    """Company profile management page (admin only)"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('company_profile.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/user-management')
@login_required
def user_management():
    """User management page (admin only)"""
    if not current_user.is_admin:
        flash('Admin access required', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('user_management.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/api/company-profile', methods=['GET', 'POST'])
@login_required
def api_company_profile():
    """Get or update company profile information"""
    if not current_user.is_admin and request.method == 'POST':
        return jsonify({'error': 'Admin access required'}), 403
    
    from models import CompanyProfile
    
    if request.method == 'GET':
        # Get company profile
        try:
            profile = CompanyProfile.query.first()
            if not profile:
                # Create default profile if not exists
                profile = CompanyProfile(
                    company_name="Your Company Name",
                    company_address="123 Main Street",
                    company_city="City",
                    company_state="State",
                    company_zip="00000",
                    company_country="Country",
                    company_phone="+1-234-567-8900",
                    company_email="info@yourcompany.com",
                    company_website="www.yourcompany.com"
                )
                db.session.add(profile)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'profile': profile.to_dict()
            })
        except Exception as e:
            print(f"[ERROR] Get company profile error: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # POST
        # Update company profile
        try:
            data = request.get_json()
            profile = CompanyProfile.query.first()
            
            if not profile:
                profile = CompanyProfile()
                db.session.add(profile)
            
            # Update fields
            if 'company_name' in data:
                profile.company_name = data['company_name']
            if 'company_address' in data:
                profile.company_address = data['company_address']
            if 'company_city' in data:
                profile.company_city = data['company_city']
            if 'company_state' in data:
                profile.company_state = data['company_state']
            if 'company_zip' in data:
                profile.company_zip = data['company_zip']
            if 'company_country' in data:
                profile.company_country = data['company_country']
            if 'company_phone' in data:
                profile.company_phone = data['company_phone']
            if 'company_email' in data:
                profile.company_email = data['company_email']
            if 'company_website' in data:
                profile.company_website = data['company_website']
            
            profile.updated_at = datetime.now()
            db.session.commit()
            
            log_event('company_profile_updated', f'Company profile updated by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': 'Company profile updated successfully',
                'profile': profile.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Update company profile error: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/upload-logo', methods=['POST'])
@login_required
def api_upload_logo():
    """Upload company logo"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from models import CompanyProfile
        from werkzeug.utils import secure_filename
        import os
        
        if 'logo' not in request.files:
            return jsonify({'error': 'No logo file provided'}), 400
        
        file = request.files['logo']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'svg'}
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, and SVG allowed'}), 400
        
        # Check file size (max 2MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 2 * 1024 * 1024:  # 2MB
            return jsonify({'error': 'File too large. Maximum size is 2MB'}), 400
        
        # Save file
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f'company_logo_{timestamp}.{file_ext}'
        file_path = os.path.join(upload_folder, new_filename)
        
        file.save(file_path)
        
        # Update database
        profile = CompanyProfile.query.first()
        if not profile:
            profile = CompanyProfile()
            db.session.add(profile)
        
        # Delete old logo file if exists
        if profile.logo_path:
            old_logo_path = os.path.join(app.root_path, 'static', profile.logo_path.lstrip('/static/'))
            if os.path.exists(old_logo_path):
                try:
                    os.remove(old_logo_path)
                except Exception as e:
                    print(f"[WARNING] Could not delete old logo: {e}")
        
        profile.logo_path = f'/static/uploads/{new_filename}'
        profile.updated_at = datetime.now()
        db.session.commit()
        
        log_event('logo_uploaded', f'Company logo uploaded by {current_user.username}')
        
        return jsonify({
            'success': True,
            'message': 'Logo uploaded successfully',
            'logo_path': profile.logo_path
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Logo upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/door-system-info', methods=['GET', 'POST'])
@login_required
def api_door_system_info():
    """Get or update door/system information"""
    if not current_user.is_admin and request.method == 'POST':
        return jsonify({'error': 'Admin access required'}), 403
    
    from models import DoorSystemInfo
    
    if request.method == 'GET':
        # Get door/system info
        try:
            info = DoorSystemInfo.query.first()
            if not info:
                # Create default info if not exists
                info = DoorSystemInfo(
                    door_location="Main Entrance",
                    department_name="Security",
                    device_serial_number="EDOMOS-001",
                    system_model="eDOMOS v2.1",
                    installation_date=datetime.now(),
                    notes="Default system configuration"
                )
                db.session.add(info)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'info': info.to_dict()
            })
        except Exception as e:
            print(f"[ERROR] Get door/system info error: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # POST
        # Update door/system info
        try:
            data = request.get_json()
            info = DoorSystemInfo.query.first()
            
            if not info:
                info = DoorSystemInfo()
                db.session.add(info)
            
            # Update fields
            if 'door_location' in data:
                info.door_location = data['door_location']
            if 'department_name' in data:
                info.department_name = data['department_name']
            if 'device_serial_number' in data:
                info.device_serial_number = data['device_serial_number']
            if 'system_model' in data:
                info.system_model = data['system_model']
            if 'installation_date' in data:
                try:
                    info.installation_date = datetime.strptime(data['installation_date'], '%Y-%m-%d')
                except:
                    pass
            if 'last_maintenance_date' in data:
                try:
                    info.last_maintenance_date = datetime.strptime(data['last_maintenance_date'], '%Y-%m-%d')
                except:
                    pass
            if 'notes' in data:
                info.notes = data['notes']
            if 'is_active' in data:
                info.is_active = bool(data['is_active'])
            
            info.updated_at = datetime.now()
            db.session.commit()
            
            log_event('system_info_updated', f'Door/system info updated by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': 'Door/system info updated successfully',
                'info': info.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Update door/system info error: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET', 'POST'])
@login_required
def api_users():
    """Get all users or create a new user"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    if request.method == 'GET':
        # Get all users
        try:
            users = User.query.all()
            return jsonify({
                'success': True,
                'users': [user.to_dict() for user in users]
            })
        except Exception as e:
            print(f"[ERROR] Get users error: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # POST
        # Create new user
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username and password are required'}), 400
            
            # Check if user already exists
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 400
            
            # Check employee_id uniqueness if provided
            if data.get('employee_id'):
                existing_employee = User.query.filter_by(employee_id=data['employee_id']).first()
                if existing_employee:
                    return jsonify({'error': 'Employee ID already exists'}), 400
            
            # Create new user
            new_user = User(
                username=data['username'],
                full_name=data.get('full_name'),
                employee_id=data.get('employee_id'),
                department=data.get('department'),
                role=data.get('role'),
                email=data.get('email'),
                phone=data.get('phone'),
                is_admin=data.get('is_admin', False),
                permissions=data.get('permissions', 'dashboard'),
                is_active=data.get('is_active', True),
                created_at=datetime.now()
            )
            new_user.set_password(data['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            log_event('user_created', f'User {new_user.username} created by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': f'User {new_user.username} created successfully',
                'user': new_user.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Create user error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_user_detail(user_id):
    """Get, update, or delete a specific user"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if request.method == 'GET':
        # Get user details
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    
    elif request.method == 'PUT':
        # Update user
        try:
            data = request.get_json()
            
            # Check employee_id uniqueness if changing
            if data.get('employee_id') and data['employee_id'] != user.employee_id:
                existing_employee = User.query.filter_by(employee_id=data['employee_id']).first()
                if existing_employee:
                    return jsonify({'error': 'Employee ID already exists'}), 400
            
            # Update fields
            if 'full_name' in data:
                user.full_name = data['full_name']
            if 'employee_id' in data:
                user.employee_id = data['employee_id']
            if 'department' in data:
                user.department = data['department']
            if 'role' in data:
                user.role = data['role']
            if 'email' in data:
                user.email = data['email']
            if 'phone' in data:
                user.phone = data['phone']
            if 'is_admin' in data:
                user.is_admin = bool(data['is_admin'])
            if 'permissions' in data:
                user.permissions = data['permissions']
            if 'is_active' in data:
                user.is_active = bool(data['is_active'])
            if 'password' in data and data['password']:
                user.set_password(data['password'])
            
            db.session.commit()
            
            log_event('user_updated', f'User {user.username} updated by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} updated successfully',
                'user': user.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Update user error: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # DELETE
        # Delete user
        try:
            if user.username == 'admin':
                return jsonify({'error': 'Cannot delete admin user'}), 403
            
            username = user.username
            db.session.delete(user)
            db.session.commit()
            
            log_event('user_deleted', f'User {username} deleted by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': f'User {username} deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Delete user error: {e}")
            return jsonify({'error': str(e)}), 500

# ==================== USER PROFILE & PREFERENCES ROUTES ====================

@app.route('/my-profile')
@login_required
def my_profile():
    """User's personal profile page"""
    return render_template('my_profile.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/api/my-profile', methods=['GET', 'PUT'])
@login_required
def api_my_profile():
    """Get or update current user's profile"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'profile': current_user.to_dict()
        })
    
    else:  # PUT
        try:
            data = request.get_json()
            
            # Update allowed fields
            if 'full_name' in data:
                current_user.full_name = data['full_name']
            if 'email' in data:
                current_user.email = data['email']
            if 'phone' in data:
                current_user.phone = data['phone']
            if 'department' in data and current_user.is_admin:
                current_user.department = data['department']
            if 'role' in data and current_user.is_admin:
                current_user.role = data['role']
            
            db.session.commit()
            
            log_event('profile_updated', f'Profile updated by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'profile': current_user.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Update profile error: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/preferences')
@login_required
def preferences():
    """User preferences page"""
    return render_template('preferences.html',
        permissions=current_user.permissions.split(',')
    )

@app.route('/api/preferences', methods=['GET', 'PUT'])
@login_required
def api_preferences():
    """Get or update user preferences"""
    from models import UserPreference
    
    if request.method == 'GET':
        # Get user preferences
        try:
            pref = UserPreference.query.filter_by(user_id=current_user.id).first()
            if not pref:
                # Create default preferences
                pref = UserPreference(
                    user_id=current_user.id,
                    theme='dark',
                    language='en',
                    timezone='UTC',
                    notifications_enabled=True,
                    email_notifications=True,
                    dashboard_refresh_rate=30
                )
                db.session.add(pref)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'preferences': pref.to_dict()
            })
        except Exception as e:
            print(f"[ERROR] Get preferences error: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # PUT
        try:
            data = request.get_json()
            pref = UserPreference.query.filter_by(user_id=current_user.id).first()
            
            if not pref:
                pref = UserPreference(user_id=current_user.id)
                db.session.add(pref)
            
            # Update preferences
            if 'theme' in data:
                pref.theme = data['theme']
            if 'language' in data:
                pref.language = data['language']
            if 'timezone' in data:
                pref.timezone = data['timezone']
            if 'notifications_enabled' in data:
                pref.notifications_enabled = bool(data['notifications_enabled'])
            if 'email_notifications' in data:
                pref.email_notifications = bool(data['email_notifications'])
            if 'dashboard_refresh_rate' in data:
                pref.dashboard_refresh_rate = int(data['dashboard_refresh_rate'])
            if 'date_format' in data:
                pref.date_format = data['date_format']
            if 'time_format' in data:
                pref.time_format = data['time_format']
            
            pref.updated_at = datetime.now()
            db.session.commit()
            
            log_event('preferences_updated', f'Preferences updated by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': 'Preferences updated successfully',
                'preferences': pref.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Update preferences error: {e}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current and new password are required'}), 400
        
        # Verify current password
        if not current_user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(data['new_password']) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        # Check if new password is same as old
        if data['current_password'] == data['new_password']:
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        # Update password
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        log_event('password_changed', f'Password changed by {current_user.username}')
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Change password error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANOMALY DETECTION & SCHEDULED REPORTS API ENDPOINTS
# ============================================================================

@app.route('/api/anomalies', methods=['GET'])
@login_required
def api_get_anomalies():
    """Get all detected anomalies with filtering options"""
    try:
        # Get query parameters
        acknowledged = request.args.get('acknowledged', None)
        anomaly_type = request.args.get('type', None)
        severity = request.args.get('severity', None)
        limit = request.args.get('limit', 50, type=int)
        
        # Build query
        query = AnomalyDetection.query
        
        if acknowledged is not None:
            ack_bool = acknowledged.lower() == 'true'
            query = query.filter(AnomalyDetection.is_acknowledged == ack_bool)
        
        if anomaly_type:
            query = query.filter(AnomalyDetection.anomaly_type == anomaly_type)
        
        if severity:
            query = query.filter(AnomalyDetection.severity == severity)
        
        # Order by most recent first
        anomalies = query.order_by(AnomalyDetection.detected_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(anomalies),
            'anomalies': [anomaly.to_dict() for anomaly in anomalies]
        })
    except Exception as e:
        print(f"[ERROR] Get anomalies error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomalies/<int:anomaly_id>/acknowledge', methods=['PUT'])
@login_required
def api_acknowledge_anomaly(anomaly_id):
    """Acknowledge an anomaly"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        anomaly = AnomalyDetection.query.get(anomaly_id)
        if not anomaly:
            return jsonify({'error': 'Anomaly not found'}), 404
        
        data = request.get_json() or {}
        
        anomaly.is_acknowledged = True
        anomaly.acknowledged_by = current_user.id
        anomaly.acknowledged_at = datetime.now()
        anomaly.notes = data.get('notes', '')
        
        db.session.commit()
        
        log_event('anomaly_acknowledged', f'Anomaly {anomaly_id} acknowledged by {current_user.username}')
        
        return jsonify({
            'success': True,
            'message': 'Anomaly acknowledged',
            'anomaly': anomaly.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Acknowledge anomaly error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomalies/stats', methods=['GET'])
@login_required
def api_anomaly_stats():
    """Get anomaly statistics"""
    try:
        total = AnomalyDetection.query.count()
        unacknowledged = AnomalyDetection.query.filter_by(is_acknowledged=False).count()
        
        # Count by type
        by_type = db.session.query(
            AnomalyDetection.anomaly_type,
            db.func.count(AnomalyDetection.id)
        ).group_by(AnomalyDetection.anomaly_type).all()
        
        # Count by severity
        by_severity = db.session.query(
            AnomalyDetection.severity,
            db.func.count(AnomalyDetection.id)
        ).group_by(AnomalyDetection.severity).all()
        
        return jsonify({
            'success': True,
            'total_anomalies': total,
            'unacknowledged': unacknowledged,
            'by_type': {t: c for t, c in by_type},
            'by_severity': {s: c for s, c in by_severity}
        })
    except Exception as e:
        print(f"[ERROR] Anomaly stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduled-reports', methods=['GET', 'POST'])
@login_required
def api_scheduled_reports():
    """Get all scheduled reports or create a new one"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    if request.method == 'GET':
        try:
            reports = ScheduledReport.query.all()
            return jsonify({
                'success': True,
                'reports': [report.to_dict() for report in reports]
            })
        except Exception as e:
            print(f"[ERROR] Get scheduled reports error: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # POST
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('report_type') or not data.get('frequency') or not data.get('recipients'):
                return jsonify({'error': 'report_type, frequency, and recipients are required'}), 400
            
            # Validate frequency
            valid_frequencies = ['daily', 'weekly', 'monthly']
            if data['frequency'] not in valid_frequencies:
                return jsonify({'error': f'frequency must be one of: {", ".join(valid_frequencies)}'}), 400
            
            # Get scheduled time (default to 09:00)
            scheduled_time = data.get('scheduled_time', '09:00')
            
            # Validate time format (HH:MM)
            try:
                hour, minute = map(int, scheduled_time.split(':'))
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    return jsonify({'error': 'Invalid time format. Use HH:MM (00:00-23:59)'}), 400
            except:
                return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
            
            # Calculate next_run based on frequency and scheduled_time
            now = datetime.now()
            if data['frequency'] == 'daily':
                next_date = now.date() + timedelta(days=1)
            elif data['frequency'] == 'weekly':
                next_date = now.date() + timedelta(days=7)
            else:  # monthly
                next_date = now.date() + timedelta(days=30)
            
            # Combine date with scheduled time
            next_run = datetime.combine(next_date, datetime.min.time()).replace(hour=hour, minute=minute)
            
            # Create new scheduled report
            import json
            report = ScheduledReport(
                report_type=data['report_type'],
                frequency=data['frequency'],
                scheduled_time=scheduled_time,
                recipients=data['recipients'],
                enabled=data.get('enabled', True),
                filters=json.dumps(data.get('filters', {})),
                next_run=next_run,
                created_by=current_user.id
            )
            
            db.session.add(report)
            db.session.commit()
            
            log_event('scheduled_report_created', f'Scheduled {data["frequency"]} {data["report_type"]} report created by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': 'Scheduled report created',
                'report': report.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Create scheduled report error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

@app.route('/api/scheduled-reports/<int:report_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_scheduled_report_detail(report_id):
    """Get, update, or delete a specific scheduled report"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    report = ScheduledReport.query.get(report_id)
    if not report:
        return jsonify({'error': 'Scheduled report not found'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'report': report.to_dict()
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update fields
            if 'report_type' in data:
                report.report_type = data['report_type']
            if 'frequency' in data:
                report.frequency = data['frequency']
            if 'recipients' in data:
                report.recipients = data['recipients']
            if 'enabled' in data:
                report.enabled = bool(data['enabled'])
            if 'filters' in data:
                import json
                report.filters = json.dumps(data['filters'])
            
            db.session.commit()
            
            log_event('scheduled_report_updated', f'Scheduled report {report_id} updated by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': 'Scheduled report updated',
                'report': report.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Update scheduled report error: {e}")
            return jsonify({'error': str(e)}), 500
    
    else:  # DELETE
        try:
            db.session.delete(report)
            db.session.commit()
            
            log_event('scheduled_report_deleted', f'Scheduled report {report_id} deleted by {current_user.username}')
            
            return jsonify({
                'success': True,
                'message': 'Scheduled report deleted'
            })
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Delete scheduled report error: {e}")
            return jsonify({'error': str(e)}), 500

# ============================================================================
# BLOCKCHAIN AUDIT TRAIL ENDPOINTS
# ============================================================================

@app.route('/api/blockchain/stats', methods=['GET'])
@login_required
def api_blockchain_stats():
    """Get blockchain statistics and verification status"""
    try:
        from blockchain_helper import get_blockchain_stats
        
        stats = get_blockchain_stats()
        
        return jsonify({
            'success': True,
            **stats
        })
    except Exception as e:
        print(f"[ERROR] Blockchain stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/verify', methods=['GET'])
@login_required
def api_blockchain_verify():
    """Verify blockchain integrity"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from blockchain_helper import verify_blockchain
        
        is_valid, message, corrupted = verify_blockchain()
        
        return jsonify({
            'success': True,
            'verified': is_valid,
            'message': message,
            'corrupted_blocks': corrupted
        })
    except Exception as e:
        print(f"[ERROR] Blockchain verify error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/events', methods=['GET'])
@login_required
def api_blockchain_events():
    """Get blockchain events with optional filters"""
    try:
        from blockchain_helper import search_blockchain
        from models import BlockchainEventLog
        
        # Get filter parameters
        event_type = request.args.get('event_type')
        description = request.args.get('description')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = BlockchainEventLog.query
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        if description:
            query = query.filter(BlockchainEventLog.description.contains(description))
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        events = query.order_by(BlockchainEventLog.block_index.desc()) \
                     .limit(limit) \
                     .offset(offset) \
                     .all()
        
        return jsonify({
            'success': True,
            'total': total,
            'events': [event.to_dict() for event in events],
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        print(f"[ERROR] Blockchain events error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/export', methods=['GET'])
@login_required
def api_blockchain_export():
    """Export blockchain for legal/compliance purposes"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from blockchain_helper import export_blockchain_proof
        
        start_index = request.args.get('start_index', type=int)
        end_index = request.args.get('end_index', type=int)
        
        proof = export_blockchain_proof(start_index, end_index)
        
        # Log the export
        log_event('blockchain_export', f'Blockchain exported by {current_user.username} (blocks {start_index or 0}-{end_index or "latest"})')
        
        return jsonify({
            'success': True,
            **proof
        })
    except Exception as e:
        print(f"[ERROR] Blockchain export error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain/block/<int:block_index>', methods=['GET'])
@login_required
def api_blockchain_block(block_index):
    """Get specific block by index"""
    try:
        from blockchain_helper import get_block_by_index
        
        block = get_block_by_index(block_index)
        
        if not block:
            return jsonify({'error': 'Block not found'}), 404
        
        return jsonify({
            'success': True,
            'block': block.to_dict()
        })
    except Exception as e:
        print(f"[ERROR] Get block error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# 21 CFR PART 11 - ELECTRONIC SIGNATURE API ENDPOINTS
# ============================================================================

@app.route('/api/signature/create', methods=['POST'])
@login_required
def api_signature_create():
    """
    Create electronic signature per 21 CFR Part 11 §11.50, §11.100, §11.200
    
    Required fields:
    - event_id: ID of the event being signed
    - event_type: Type of event (change_control, training, approval, etc.)
    - action: Description of action being signed
    - reason: User's reason for signing (required per §11.50)
    - password: User's password for identity verification (required per §11.200)
    """
    try:
        from models import ElectronicSignature
        from blockchain_helper import add_blockchain_event
        import hashlib
        from werkzeug.security import check_password_hash
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_id', 'event_type', 'action', 'reason', 'password']
        missing_fields = [f for f in required_fields if not data.get(f)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Verify password (identity verification per §11.200)
        if not check_password_hash(current_user.password_hash, data['password']):
            return jsonify({
                'success': False,
                'message': 'Incorrect password. Electronic signature requires valid password for identity verification.'
            }), 401
        
        # Validate reason length
        reason = data['reason'].strip()
        if len(reason) < 10:
            return jsonify({
                'success': False,
                'message': 'Reason for signing must be at least 10 characters (required per 21 CFR Part 11 §11.50)'
            }), 400
        
        # Get IP address
        ip_address = request.remote_addr or 'Unknown'
        if request.headers.get('X-Forwarded-For'):
            ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        
        # Generate signature hash (SHA-256 of user_id + timestamp + reason + event_id)
        timestamp = datetime.utcnow()
        hash_input = f"{current_user.id}:{timestamp.isoformat()}:{reason}:{data['event_id']}:{data['event_type']}"
        signature_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Create signature record
        signature = ElectronicSignature(
            user_id=current_user.id,
            event_id=data['event_id'],
            event_type=data['event_type'],
            action=data['action'],
            reason=reason,
            signature_hash=signature_hash,
            ip_address=ip_address,
            timestamp=timestamp
        )
        
        db.session.add(signature)
        db.session.commit()
        
        # Add to blockchain for immutability
        # Description includes key metadata since blockchain doesn't support metadata parameter
        blockchain_description = (
            f"E-Signature: {data['action']} | "
            f"Event: {data['event_id']} ({data['event_type']}) | "
            f"Hash: {signature_hash[:16]}... | "
            f"Reason: {reason[:50]}{'...' if len(reason) > 50 else ''}"
        )
        add_blockchain_event(
            event_type='electronic_signature',
            description=blockchain_description,
            user_id=current_user.id,
            ip_address=ip_address
        )
        
        print(f"[SIGNATURE] Created e-signature {signature.id} for user {current_user.username} - {data['action']}")
        
        return jsonify({
            'success': True,
            'message': 'Electronic signature created successfully',
            'signature': {
                'id': signature.id,
                'signature_hash': signature_hash,
                'timestamp': timestamp.isoformat(),
                'user': current_user.username,
                'ip_address': ip_address
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Signature creation error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Failed to create signature: {str(e)}'
        }), 500

@app.route('/api/signature/verify/<int:signature_id>', methods=['GET'])
@login_required
def api_signature_verify(signature_id):
    """
    Verify electronic signature integrity and retrieve details
    """
    try:
        from models import ElectronicSignature
        
        signature = db.session.query(ElectronicSignature).filter_by(id=signature_id).first()
        
        if not signature:
            return jsonify({
                'success': False,
                'message': 'Signature not found'
            }), 404
        
        return jsonify({
            'success': True,
            'signature': signature.to_dict()
        })
        
    except Exception as e:
        print(f"[ERROR] Signature verification error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/signature/by-event/<int:event_id>', methods=['GET'])
@login_required
def api_signature_by_event(event_id):
    """
    Get all signatures for a specific event
    Query params: event_type (optional)
    """
    try:
        from models import ElectronicSignature
        
        event_type = request.args.get('event_type')
        
        query = db.session.query(ElectronicSignature).filter_by(event_id=event_id)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        signatures = query.order_by(ElectronicSignature.timestamp.desc()).all()
        
        return jsonify({
            'success': True,
            'count': len(signatures),
            'signatures': [sig.to_dict() for sig in signatures]
        })
        
    except Exception as e:
        print(f"[ERROR] Get signatures by event error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/signature/user/<int:user_id>', methods=['GET'])
@login_required
def api_signature_by_user(user_id):
    """
    Get all signatures by a specific user
    Query params: limit (default 50), offset (default 0)
    """
    try:
        from models import ElectronicSignature
        
        # Only admins can view other users' signatures
        if current_user.role != 'admin' and current_user.id != user_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized. Only admins can view other users signatures.'
            }), 403
        
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))
        
        signatures = db.session.query(ElectronicSignature)\
            .filter_by(user_id=user_id)\
            .order_by(ElectronicSignature.timestamp.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        total = db.session.query(ElectronicSignature).filter_by(user_id=user_id).count()
        
        return jsonify({
            'success': True,
            'count': len(signatures),
            'total': total,
            'signatures': [sig.to_dict() for sig in signatures]
        })
        
    except Exception as e:
        print(f"[ERROR] Get signatures by user error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ============================================================================
# STRESS TESTING & LOAD TESTING ENDPOINTS (For Locust Testing)
# ============================================================================

@app.route('/api/test/endpoints', methods=['GET'])
def get_test_endpoints():
    """
    Returns a comprehensive list of all API endpoints for stress testing.
    This endpoint does NOT require authentication.
    
    Returns JSON with endpoints categorized by authentication requirement.
    """
    endpoints = {
        "test_info": {
            "description": "eDOMOS API Endpoints for Load Testing",
            "version": "2.1",
            "server": request.host,
            "timestamp": datetime.now().isoformat()
        },
        "public_endpoints": {
            "description": "Endpoints that do NOT require authentication",
            "endpoints": [
                {
                    "path": "/api/test/health",
                    "methods": ["GET"],
                    "description": "Health check endpoint for load testing",
                    "expected_response": {"status": "ok", "timestamp": "ISO8601"}
                },
                {
                    "path": "/api/test/ping",
                    "methods": ["GET"],
                    "description": "Simple ping endpoint",
                    "expected_response": {"ping": "pong"}
                },
                {
                    "path": "/login",
                    "methods": ["GET", "POST"],
                    "description": "Login page/endpoint",
                    "note": "POST requires username and password"
                },
                {
                    "path": "/websocket-test",
                    "methods": ["GET"],
                    "description": "WebSocket test page"
                },
                {
                    "path": "/",
                    "methods": ["GET"],
                    "description": "Home page (redirects to login or dashboard)"
                }
            ]
        },
        "authenticated_endpoints": {
            "description": "Endpoints that REQUIRE authentication (login first)",
            "note": "Use /login endpoint to get session cookie, then use it in subsequent requests",
            "test_credentials": {
                "username": "admin",
                "password": "admin123",
                "method": "POST",
                "url": "/login",
                "body": {"username": "admin", "password": "admin123"}
            },
            "endpoints": [
                {
                    "path": "/dashboard",
                    "methods": ["GET"],
                    "description": "Main dashboard page"
                },
                {
                    "path": "/api/dashboard",
                    "methods": ["GET"],
                    "description": "Dashboard data API"
                },
                {
                    "path": "/api/status",
                    "methods": ["GET"],
                    "description": "Current door and alarm status"
                },
                {
                    "path": "/api/uptime",
                    "methods": ["GET"],
                    "description": "System uptime information"
                },
                {
                    "path": "/api/events",
                    "methods": ["GET"],
                    "description": "Event log data"
                },
                {
                    "path": "/api/statistics",
                    "methods": ["GET"],
                    "description": "System statistics"
                },
                {
                    "path": "/api/analytics/data",
                    "methods": ["GET"],
                    "description": "Analytics data for charts"
                },
                {
                    "path": "/api/company-profile",
                    "methods": ["GET", "POST"],
                    "description": "Company profile information"
                },
                {
                    "path": "/api/door-system-info",
                    "methods": ["GET", "POST"],
                    "description": "Door system configuration"
                },
                {
                    "path": "/api/users",
                    "methods": ["GET", "POST"],
                    "description": "User management API"
                },
                {
                    "path": "/event-log",
                    "methods": ["GET"],
                    "description": "Event log page"
                },
                {
                    "path": "/analytics",
                    "methods": ["GET"],
                    "description": "Analytics page"
                },
                {
                    "path": "/reports",
                    "methods": ["GET"],
                    "description": "Reports page"
                }
            ]
        },
        "load_testing_tips": {
            "session_management": "Use requests.Session() to maintain cookies across requests",
            "authentication_flow": "1. POST to /login with credentials, 2. Save session cookie, 3. Use cookie in subsequent requests",
            "rate_limiting": "No rate limiting implemented - test responsibly",
            "websocket_testing": "WebSocket endpoint: ws://{host}/socket.io/?EIO=4&transport=websocket&ns=/events",
            "recommended_tests": [
                "Read-only endpoints (GET /api/status, /api/dashboard)",
                "Event log queries with filters",
                "Analytics data retrieval",
                "Multiple concurrent authenticated sessions"
            ]
        }
    }
    
    return jsonify(endpoints), 200


@app.route('/api/test/health', methods=['GET'])
def test_health():
    """
    Health check endpoint for load testing.
    Does NOT require authentication.
    Returns basic system health information.
    """
    try:
        # Check database connectivity
        db_status = "ok"
        try:
            db.session.execute('SELECT 1')
            db.session.commit()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Check GPIO status
        gpio_status = "ok"
        try:
            door_state = GPIO.input(DOOR_SENSOR_PIN)
        except Exception as e:
            gpio_status = f"error: {str(e)}"
        
        # Calculate uptime
        uptime_seconds = (datetime.now() - SERVER_START_TIME).total_seconds()
        
        health_data = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "database": db_status,
            "gpio": gpio_status,
            "version": "2.1",
            "service": "eDOMOS Door Alarm System"
        }
        
        return jsonify(health_data), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/test/ping', methods=['GET'])
def test_ping():
    """
    Simple ping endpoint for load testing.
    Does NOT require authentication.
    Returns minimal response for basic connectivity testing.
    """
    return jsonify({
        "ping": "pong",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/test/auth-check', methods=['GET'])
@login_required
def test_auth_check():
    """
    Test endpoint to verify authentication is working.
    REQUIRES authentication.
    Use this to test if your session cookie is valid.
    """
    return jsonify({
        "authenticated": True,
        "user": current_user.username,
        "user_id": current_user.id,
        "is_admin": current_user.is_admin,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/test/stress-data', methods=['GET'])
def test_stress_data():
    """
    Returns mock data for stress testing without hitting the database.
    Does NOT require authentication.
    Useful for testing pure application server performance.
    """
    mock_data = {
        "door_status": "Closed",
        "alarm_status": "Off",
        "timer_active": False,
        "events_count": 1250,
        "last_event": datetime.now().isoformat(),
        "system_health": "Excellent",
        "cpu_usage": "25%",
        "memory_usage": "340MB",
        "mock": True,
        "note": "This is mock data for stress testing"
    }
    return jsonify(mock_data), 200


# ============================================================================
# END OF STRESS TESTING ENDPOINTS
# ============================================================================

# ============================================================================
# SCHEDULED REPORTS SYSTEM
# ============================================================================

report_scheduler_thread = None

def report_scheduler():
    """Background thread to check and send scheduled reports"""
    global shutdown_flag
    print("[SCHEDULER] 📧 Report scheduler thread started")
    
    while not shutdown_flag.is_set():
        try:
            with app.app_context():
                now = datetime.now()
                
                # Find all enabled scheduled reports that are due
                due_reports = ScheduledReport.query.filter(
                    ScheduledReport.enabled == True,
                    ScheduledReport.next_run <= now
                ).all()
                
                for report in due_reports:
                    print(f"[SCHEDULER] 📊 Processing scheduled report: {report.report_type} ({report.frequency})")
                    
                    try:
                        # Generate report based on frequency
                        if report.frequency == 'daily':
                            start_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
                            end_date = now.strftime('%Y-%m-%d')
                        elif report.frequency == 'weekly':
                            start_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                            end_date = now.strftime('%Y-%m-%d')
                        elif report.frequency == 'monthly':
                            start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
                            end_date = now.strftime('%Y-%m-%d')
                        else:
                            start_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
                            end_date = now.strftime('%Y-%m-%d')
                        
                        # Parse filters if available
                        import json
                        filters = json.loads(report.filters) if report.filters else {}
                        event_types = filters.get('event_types', ['door_open', 'door_close', 'alarm_triggered'])
                        
                        # Generate PDF report
                        pdf_buffer = generate_scheduled_report_pdf(
                            start_date=start_date,
                            end_date=end_date,
                            event_types=event_types,
                            report_type=report.report_type
                        )
                        
                        # Send email with PDF attachment
                        send_scheduled_report_email(
                            report=report,
                            pdf_buffer=pdf_buffer,
                            start_date=start_date,
                            end_date=end_date
                        )
                        
                        # Update report schedule with scheduled_time
                        report.last_run = now
                        
                        # Parse scheduled time (HH:MM format)
                        scheduled_time = report.scheduled_time or '09:00'
                        hour, minute = map(int, scheduled_time.split(':'))
                        
                        # Calculate next run based on frequency
                        if report.frequency == 'daily':
                            next_date = now.date() + timedelta(days=1)
                        elif report.frequency == 'weekly':
                            next_date = now.date() + timedelta(days=7)
                        elif report.frequency == 'monthly':
                            next_date = now.date() + timedelta(days=30)
                        else:
                            next_date = now.date() + timedelta(days=1)
                        
                        # Combine date with scheduled time
                        report.next_run = datetime.combine(next_date, datetime.min.time()).replace(hour=hour, minute=minute)
                        
                        db.session.commit()
                        print(f"[SCHEDULER] ✅ Report sent successfully: {report.report_type}, Next run: {report.next_run}")
                        
                    except Exception as e:
                        print(f"[SCHEDULER] ❌ Failed to send report {report.id}: {e}")
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
            
        except Exception as e:
            print(f"[SCHEDULER] ❌ Scheduler error: {e}")
            import traceback
            traceback.print_exc()
        
        # Check every hour
        time.sleep(3600)
    
    print("[SCHEDULER] 📧 Report scheduler thread exiting...")

def generate_scheduled_report_pdf(start_date, end_date, event_types, report_type):
    """Generate PDF report for scheduled delivery"""
    from io import BytesIO
    from models import CompanyProfile, DoorSystemInfo
    
    try:
        # Query events for the date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        query = EventLog.query.filter(EventLog.timestamp.between(start_dt, end_dt))
        if event_types:
            query = query.filter(EventLog.event_type.in_(event_types))
        
        events = query.all()
        
        # Get company and system info
        company_profile = CompanyProfile.query.first()
        door_system_info = DoorSystemInfo.query.first()
        
        # Prepare data dict similar to generate_report route
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'event_types': event_types or [],
            'report_type': report_type,
            'format': 'pdf'
        }
        
        # Import PDF libraries
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        buffer = BytesIO()
        
        # Create simplified PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
            title=f"eDOMOS {report_type.title()} Report - {start_date} to {end_date}"
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=20,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(f"eDOMOS {report_type.title()} Report", title_style))
        story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary statistics
        summary_data = [
            ['Total Events', str(len(events))],
            ['Report Type', report_type.title()],
            ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Events table
        if events:
            story.append(Paragraph("Event Details", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            event_data = [['Date/Time', 'Event Type', 'Description']]
            
            for event in events[:100]:  # Limit to 100 events for email
                event_data.append([
                    event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    event.event_type.replace('_', ' ').title(),
                    event.description or '-'
                ])
            
            event_table = Table(event_data, colWidths=[2*inch, 2*inch, 1.5*inch])
            event_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
            ]))
            
            story.append(event_table)
        else:
            story.append(Paragraph("No events found for the selected period.", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        print(f"[SCHEDULER] 📄 PDF generated: {len(buffer.getvalue())} bytes, {len(events)} events")
        return buffer
        
    except Exception as e:
        print(f"[SCHEDULER] ❌ PDF generation failed: {e}")
        print(f"[SCHEDULER] 🔍 Error details: {traceback.format_exc()}")
        return None

def send_scheduled_report_email(report, pdf_buffer, start_date, end_date):
    """Send scheduled report via email with PDF attachment"""
    try:
        email_config = EmailConfig.query.first()
        if not email_config or not email_config.is_configured:
            print("[SCHEDULER] ❌ Email not configured, skipping")
            return False
        
        recipients = [email.strip() for email in report.recipients.split(',')]
        print(f"[SCHEDULER] 📧 Preparing email for {len(recipients)} recipients: {recipients}")
        
        msg = MIMEMultipart()
        msg['From'] = email_config.sender_email
        msg['To'] = report.recipients
        msg['Subject'] = f"eDOMOS {report.report_type.title()} Report - {start_date} to {end_date}"
        
        body = f"""
📊 Scheduled {report.report_type.title()} Report

📅 Report Period: {start_date} to {end_date}
🔄 Frequency: {report.frequency.title()}
📧 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated report from the eDOMOS Door Monitoring System.
Please find the detailed report attached as a PDF.

---
eDOMOS v2.1 - Door Alarm & Monitoring System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        if pdf_buffer and pdf_buffer.getvalue():
            pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), _subtype="pdf")
            pdf_filename = f'eDOMOS_Report_{start_date}_to_{end_date}.pdf'
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
            msg.attach(pdf_attachment)
            print(f"[SCHEDULER] 📎 PDF attached: {pdf_filename} ({len(pdf_buffer.getvalue())} bytes)")
        else:
            print("[SCHEDULER] ⚠️ No PDF buffer provided, sending email without attachment")
        
        # Send email using Gmail SMTP
        print(f"[SCHEDULER] 🔗 Connecting to SMTP server (smtp.gmail.com:587)...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print(f"[SCHEDULER] 🔐 Logging in as {email_config.sender_email}...")
        server.login(email_config.sender_email, email_config.app_password)
        print(f"[SCHEDULER] 📤 Sending email...")
        server.sendmail(email_config.sender_email, recipients, msg.as_string())
        server.quit()
        
        print(f"[SCHEDULER] ✅ Report emailed successfully to {len(recipients)} recipients")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[SCHEDULER] ❌ SMTP Authentication failed: {e}")
        print("[SCHEDULER] 💡 Check email and app password in System Configuration")
        return False
    except smtplib.SMTPException as e:
        print(f"[SCHEDULER] ❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[SCHEDULER] ❌ Email sending failed: {e}")
        print(f"[SCHEDULER] 🔍 Error details: {traceback.format_exc()}")
        return False

def start_report_scheduler():
    """Start the report scheduler thread"""
    global report_scheduler_thread
    if not report_scheduler_thread or not report_scheduler_thread.is_alive():
        report_scheduler_thread = threading.Thread(target=report_scheduler, name="ReportScheduler")
        report_scheduler_thread.daemon = True
        report_scheduler_thread.start()
        print("📧 Report scheduler thread started")
    else:
        print("⚠️ Report scheduler already running")

# Start door monitoring in a separate thread
monitor_thread_lock = threading.Lock()

def start_monitoring():
    global monitor_thread
    with monitor_thread_lock:
        if not monitor_thread or not monitor_thread.is_alive():
            monitor_thread = threading.Thread(target=monitor_door, name="DoorMonitor")
            monitor_thread.daemon = True
            monitor_thread.start()
            print("🔍 Door monitoring thread started")
        else:
            print("⚠️ Door monitoring thread already running")

# Remove duplicate cleanup function as we already have one above

if __name__ == '__main__':
    atexit.register(cleanup_and_exit)
    
    # ============================================================================
    # SSL CERTIFICATE CONFIGURATION
    # ============================================================================
    
    # SSL certificate paths
    SSL_DIR = os.path.join(BASE_DIR, 'ssl')
    SSL_CERT = os.path.join(SSL_DIR, 'cert.pem')
    SSL_KEY = os.path.join(SSL_DIR, 'key.pem')
    
    # Check if SSL should be enabled (via environment variable)
    use_ssl_env = os.environ.get('USE_SSL', 'false').lower() == 'true'
    ssl_certs_exist = os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY)
    ssl_enabled = use_ssl_env and ssl_certs_exist
    
    if ssl_enabled:
        print("🔐 SSL enabled - HTTPS mode")
        protocol = "https"
        ws_protocol = "wss"
    elif ssl_certs_exist and not use_ssl_env:
        print("🌐 SSL disabled - HTTP mode (default)")
        print("💡 To enable HTTPS: USE_SSL=true python app.py")
        protocol = "http"
        ws_protocol = "ws"
    else:
        print("⚠️  SSL certificates not found - Running on HTTP")
        print("💡 Run './generate_ssl_cert.sh' to generate SSL certificates")
        protocol = "http"
        ws_protocol = "ws"
    
    print("�🚀 Starting eDOMOS-v2 Door Alarm System...")
    print("📡 WebSocket support enabled")
    print("🔄 Event-driven real-time updates active")
    print(f"🌐 Server will be available at: {protocol}://0.0.0.0:5000")
    print(f"🔌 WebSocket endpoint: {ws_protocol}://0.0.0.0:5000/socket.io/?EIO=4&transport=websocket&ns=/events")
    
    if ssl_enabled:
        print(f"🔒 SSL Certificate: {SSL_CERT}")
        print(f"🔑 SSL Private Key: {SSL_KEY}")
        print("⚠️  Self-signed certificate - Browser will show security warning")
    
    print("=" * 60)
    
    try:
        init_system()
        start_monitoring()
        start_report_scheduler()  # Start scheduled reports system
        
        # Enhanced SocketIO configuration for better connection handling
        print("🔧 Starting SocketIO server with enhanced configuration...")
        
        if ssl_enabled:
            # Run with SSL/TLS encryption
            # Flask-SocketIO requires ssl_context parameter, not certfile/keyfile
            import ssl
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(SSL_CERT, SSL_KEY)
            
            socketio.run(
                app, 
                host='0.0.0.0', 
                port=5000, 
                debug=False,
                use_reloader=False,  # Prevent double initialization
                log_output=False,     # Disable SocketIO logging to prevent WSGI errors
                allow_unsafe_werkzeug=True,  # Allow development server
                ssl_context=ssl_context  # SSL context with certificate and key
            )
        else:
            # Run without SSL (HTTP only)
            socketio.run(
                app, 
                host='0.0.0.0', 
                port=5000, 
                debug=False,
                use_reloader=False,  # Prevent double initialization
                log_output=False,     # Disable SocketIO logging to prevent WSGI errors
                allow_unsafe_werkzeug=True  # Allow development server
            )
    except KeyboardInterrupt:
        print("\n[DEBUG] 🛑 Keyboard interrupt received")
        cleanup_and_exit()
    except Exception as e:
        print(f"[ERROR] ❌ Application error: {e}")
        cleanup_and_exit()
    finally:
        cleanup_and_exit()
