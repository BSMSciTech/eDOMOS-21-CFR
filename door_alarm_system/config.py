import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///alarm_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Session timeout
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # Email configuration (will be set by admin)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or ''
    RECIPIENT_EMAILS = []  # Will be populated from database
    
    # Camera configuration
    CAMERA_CONFIG = {
        'enabled': True,              # Enable/disable camera feature
        'required': False,            # Don't fail if camera unavailable
        'type': 'usb',               # 'usb' for webcam, 'picamera' for Pi Camera Module
        'device_index': 0,            # USB camera device number (usually 0)
        'resolution': (1920, 1080),   # Image resolution (1920x1080, 1280x720, or 640x480)
        'quality': 85,                # JPEG quality 1-100
        'storage_path': 'static/captures',  # Where to save images
        'auto_detect': True,          # Auto-detect camera on startup
        'capture_on_open': True,      # Capture image when door opens
        'capture_on_close': True,     # Capture image when door closes
        'capture_on_alarm': True,     # Capture image when alarm triggers
        'retention_days': 90,         # Delete images older than this
        'max_storage_gb': 50,         # Maximum storage for images (GB)
        'timestamp_overlay': False,   # Add timestamp text to image (optional)
    }