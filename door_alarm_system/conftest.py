"""
Pytest Configuration for eDOMOS Industrial Testing
=================================================
Shared fixtures and configuration for all test modules
"""

import pytest
import os
import sys
import tempfile
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock GPIO before importing app if running on non-Raspberry Pi
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    # Mock GPIO module for testing on non-RPi systems
    from unittest.mock import MagicMock
    sys.modules['RPi.GPIO'] = MagicMock()
    sys.modules['RPi'] = MagicMock()

from app import app as flask_app, db as database
from models import User, Setting, EventLog, CompanyProfile, DoorSystemInfo
from config import Config
from sqlalchemy.exc import IntegrityError


@pytest.fixture(scope='function')
def app():
    """Create and configure Flask app for testing - fresh database for each test"""
    # Use in-memory SQLite database for testing
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    flask_app.config['SERVER_NAME'] = 'localhost.localdomain'
    
    # Create application context
    with flask_app.app_context():
        # Drop all tables first to ensure clean state
        database.drop_all()
        
        # Create all tables
        database.create_all()
        
        # Create test admin user - check if exists first
        admin = User.query.filter_by(username='testadmin').first()
        if not admin:
            admin = User(
                username='testadmin',
                full_name='Test Administrator',
                email='admin@test.com',
                is_admin=True,
                approval_level='admin',
                permissions='all,controls,dashboard,reports,change_control,validation,training,settings'
            )
            admin.set_password('TestAdmin123!')
            database.session.add(admin)
        
        # Create test regular user
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(
                username='testuser',
                full_name='Test User',
                email='user@test.com',
                is_admin=False,
                approval_level='user',
                permissions='dashboard,reports'
            )
            user.set_password('TestUser123!')
            database.session.add(user)
        
        # Create test supervisor
        supervisor = User.query.filter_by(username='testsupervisor').first()
        if not supervisor:
            supervisor = User(
                username='testsupervisor',
                full_name='Test Supervisor',
                email='supervisor@test.com',
                is_admin=False,
                approval_level='supervisor',
                permissions='dashboard,reports,change_control'
            )
            supervisor.set_password('TestSuper123!')
            database.session.add(supervisor)
        
        # Create default settings - idempotent and resilient to unique constraint
        settings_data = [
            ('timer_duration', '5'),
            ('timer_delay', '5'),  # Legacy compatibility
            ('email_notifications', 'true'),
            ('ai_enabled', 'true'),
            ('blockchain_enabled', 'true'),
            ('ip_restriction_enabled', 'false'),
            ('ip_whitelist', ''),
            ('ip_blacklist', ''),
            ('business_hours_start', '08'),
            ('business_hours_end', '18'),
        ]

        for key, value in settings_data:
            # Try to find existing setting first
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                # Ensure value is present and up-to-date
                setting.value = value
                database.session.add(setting)
                # flush to catch any immediate constraint issues
                try:
                    database.session.flush()
                except IntegrityError:
                    database.session.rollback()
                    # Re-fetch and continue
                    setting = Setting.query.filter_by(key=key).first()
                    if setting:
                        setting.value = value
                        database.session.add(setting)
            else:
                # Create a new setting entry; flush immediately to catch duplicates
                try:
                    database.session.add(Setting(key=key, value=value))
                    database.session.flush()
                except IntegrityError:
                    # Another parallel operation may have created it; rollback and ensure value
                    database.session.rollback()
                    existing = Setting.query.filter_by(key=key).first()
                    if existing:
                        existing.value = value
                        database.session.add(existing)
        
        # Create company profile
        company = CompanyProfile.query.first()
        if not company:
            company = CompanyProfile(
                company_name='Test Pharmaceutical Inc.',
                company_address='123 Test Street',
                company_city='Test City',
                company_state='TS',
                company_country='USA',
                company_email='info@testpharma.com'
            )
            database.session.add(company)
        
        # Create door system info
        door_info = DoorSystemInfo.query.first()
        if not door_info:
            door_info = DoorSystemInfo(
                door_location='Cleanroom A - Main Entrance',
                department_name='Production',
                device_serial_number='EDOMOS-TEST-001',
                system_model='eDOMOS v2.1'
            )
            database.session.add(door_info)
        
        try:
            database.session.commit()
        except Exception as e:
            database.session.rollback()
            print(f"Error setting up test data: {e}")
        
        yield flask_app
        
        # Cleanup
        database.session.remove()
        database.drop_all()


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Database session for testing"""
    with app.app_context():
        yield database.session
        database.session.rollback()


@pytest.fixture
def admin_auth(client):
    """Authenticated admin session"""
    with client:
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'TestAdmin123!'
        }, follow_redirects=True)
        yield client


@pytest.fixture
def user_auth(client):
    """Authenticated user session"""
    with client:
        client.post('/login', data={
            'username': 'testuser',
            'password': 'TestUser123!'
        }, follow_redirects=True)
        yield client


@pytest.fixture
def supervisor_auth(client):
    """Authenticated supervisor session"""
    with client:
        client.post('/login', data={
            'username': 'testsupervisor',
            'password': 'TestSuper123!'
        }, follow_redirects=True)
        yield client


@pytest.fixture
def sample_event(db_session):
    """Create sample event log entry"""
    event = EventLog(
        event_type='door_open',
        description='Test door open event',
        timestamp=datetime.utcnow()
    )
    db_session.add(event)
    db_session.commit()
    return event


@pytest.fixture
def mock_gpio():
    """Mock GPIO for testing without hardware"""
    class MockGPIO:
        BCM = 'BCM'
        IN = 'IN'
        OUT = 'OUT'
        PUD_UP = 'PUD_UP'
        RISING = 'RISING'
        FALLING = 'FALLING'
        HIGH = 1
        LOW = 0
        
        @staticmethod
        def setmode(mode):
            pass
        
        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            pass
        
        @staticmethod
        def input(pin):
            return MockGPIO.HIGH
        
        @staticmethod
        def output(pin, state):
            pass
        
        @staticmethod
        def add_event_detect(pin, edge, callback=None, bouncetime=None):
            pass
        
        @staticmethod
        def cleanup():
            pass
    
    return MockGPIO()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for system components"
    )
    config.addinivalue_line(
        "markers", "security: Security and compliance tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "cfr: 21 CFR Part 11 compliance tests"
    )
