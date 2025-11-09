from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    permissions = db.Column(db.String(200), default="dashboard")  # Comma-separated list
    
    # Extended User Profile Fields
    full_name = db.Column(db.String(150))
    employee_id = db.Column(db.String(50))  # Removed unique=True for SQLite compatibility
    department = db.Column(db.String(100))
    role = db.Column(db.String(100))
    approval_level = db.Column(db.String(20), default='user')  # 'user', 'supervisor', 'manager', 'director', 'admin'
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Password Management Fields (21 CFR Part 11 Compliance)
    password_reset_required = db.Column(db.Boolean, default=False)  # Force password change on next login
    password_reset_token = db.Column(db.String(100))  # Temporary password token
    password_reset_expires = db.Column(db.DateTime)  # Token expiration
    password_changed_at = db.Column(db.DateTime)  # Last password change date
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
        self.password_reset_required = False  # Clear reset flag when password is changed
        self.password_reset_token = None  # Clear any temporary tokens
        self.password_reset_expires = None
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'employee_id': self.employee_id,
            'department': self.department,
            'role': self.role,
            'email': self.email,
            'phone': self.phone,
            'permissions': self.permissions,
            'approval_level': self.approval_level,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'password_reset_required': self.password_reset_required,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
            'password_changed_at': self.password_changed_at.strftime('%Y-%m-%d %H:%M:%S') if self.password_changed_at else None
        }

class CompanyProfile(db.Model):
    """Company/Organization information"""
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    company_address = db.Column(db.Text)
    company_city = db.Column(db.String(100))
    company_state = db.Column(db.String(100))
    company_zip = db.Column(db.String(20))
    company_country = db.Column(db.String(100))
    company_phone = db.Column(db.String(20))
    company_email = db.Column(db.String(120))
    company_website = db.Column(db.String(200))
    logo_path = db.Column(db.String(500))  # Path to uploaded logo
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_address': self.company_address,
            'company_city': self.company_city,
            'company_state': self.company_state,
            'company_zip': self.company_zip,
            'company_country': self.company_country,
            'company_phone': self.company_phone,
            'company_email': self.company_email,
            'company_website': self.company_website,
            'logo_path': self.logo_path,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class DoorSystemInfo(db.Model):
    """Door and system-specific information"""
    id = db.Column(db.Integer, primary_key=True)
    door_location = db.Column(db.String(200), nullable=False)
    department_name = db.Column(db.String(100))
    device_serial_number = db.Column(db.String(100), unique=True)
    system_model = db.Column(db.String(100), default="eDOMOS v2.1")
    installation_date = db.Column(db.Date)
    last_maintenance_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'door_location': self.door_location,
            'department_name': self.department_name,
            'device_serial_number': self.device_serial_number,
            'system_model': self.system_model,
            'installation_date': self.installation_date.strftime('%Y-%m-%d') if self.installation_date else None,
            'last_maintenance_date': self.last_maintenance_date.strftime('%Y-%m-%d') if self.last_maintenance_date else None,
            'notes': self.notes,
            'is_active': self.is_active,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # 'door_open', 'door_close', 'alarm_triggered', 'setting_changed'
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Camera capture fields
    image_path = db.Column(db.String(500))  # Path to captured image
    image_hash = db.Column(db.String(64))   # SHA-256 hash for verification
    image_timestamp = db.Column(db.DateTime)  # When image was captured
    
    # AI Analysis metadata (JSON string)
    ai_metadata = db.Column(db.Text)  # Stores AI analysis results
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'image_path': self.image_path,
            'image_hash': self.image_hash,
            'image_timestamp': self.image_timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.image_timestamp else None,
            'has_image': bool(self.image_path),
            'ai_metadata': self.ai_metadata
        }

class BlockchainEventLog(db.Model):
    """Blockchain-verified immutable event log for compliance and security"""
    __tablename__ = 'blockchain_event_log'
    
    id = db.Column(db.Integer, primary_key=True)
    block_index = db.Column(db.Integer, nullable=False, unique=True)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Blockchain fields
    block_hash = db.Column(db.String(64), nullable=False, unique=True)
    previous_hash = db.Column(db.String(64), nullable=False)
    nonce = db.Column(db.Integer, default=0)
    
    # Metadata
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'block_index': self.block_index,
            'event_type': self.event_type,
            'description': self.description,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'block_hash': self.block_hash,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'user_id': self.user_id,
            'ip_address': self.ip_address
        }
    
    def calculate_hash(self):
        """Calculate the hash for this block"""
        import hashlib
        import json
        
        block_data = {
            'block_index': self.block_index,
            'event_type': self.event_type,
            'description': self.description,
            'timestamp': self.timestamp.isoformat() if self.timestamp else '',
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'user_id': self.user_id
        }
        
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class UserPreference(db.Model):
    """User preferences and settings"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(20), default='dark')  # 'light' or 'dark'
    language = db.Column(db.String(10), default='en')  # 'en', 'es', 'fr', etc.
    timezone = db.Column(db.String(50), default='UTC')
    notifications_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    dashboard_refresh_rate = db.Column(db.Integer, default=30)  # seconds
    date_format = db.Column(db.String(20), default='YYYY-MM-DD')
    time_format = db.Column(db.String(20), default='24h')  # '12h' or '24h'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('preference', uselist=False))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'timezone': self.timezone,
            'notifications_enabled': self.notifications_enabled,
            'email_notifications': self.email_notifications,
            'dashboard_refresh_rate': self.dashboard_refresh_rate,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class EmailConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_email = db.Column(db.String(120), nullable=False)
    app_password = db.Column(db.String(100), nullable=False)
    recipient_emails = db.Column(db.Text, nullable=False)  # Comma-separated emails
    is_configured = db.Column(db.Boolean, default=False)

class AnomalyDetection(db.Model):
    """Anomaly detection for unusual door access patterns"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event_log.id'), nullable=True)
    anomaly_type = db.Column(db.String(50), nullable=False)  # odd_hours, repeated_opens, prolonged_open
    severity = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high
    description = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)
    
    # Relationship
    event = db.relationship('EventLog', backref='anomalies')
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'anomaly_type': self.anomaly_type,
            'severity': self.severity,
            'description': self.description,
            'detected_at': self.detected_at.strftime('%Y-%m-%d %H:%M:%S') if self.detected_at else None,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.strftime('%Y-%m-%d %H:%M:%S') if self.acknowledged_at else None,
            'notes': self.notes
        }

class ScheduledReport(db.Model):
    """Scheduled automated reports (daily/weekly summaries)"""
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # summary, compliance, custom
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    scheduled_time = db.Column(db.String(5), default='09:00')  # Time to send report (HH:MM format)
    recipients = db.Column(db.Text, nullable=False)  # Comma-separated email addresses
    enabled = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime, nullable=True)
    next_run = db.Column(db.DateTime, nullable=True)
    filters = db.Column(db.Text, nullable=True)  # JSON string for event filters
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    creator = db.relationship('User', backref='scheduled_reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_type': self.report_type,
            'frequency': self.frequency,
            'scheduled_time': self.scheduled_time,
            'recipients': self.recipients,
            'enabled': self.enabled,
            'last_run': self.last_run.strftime('%Y-%m-%d %H:%M:%S') if self.last_run else None,
            'next_run': self.next_run.strftime('%Y-%m-%d %H:%M:%S') if self.next_run else None,
            'filters': self.filters,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class License(db.Model):
    """Software license and restrictions"""
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(100), unique=True, nullable=False)
    license_type = db.Column(db.String(50), nullable=False)  # 'starter', 'professional', 'enterprise', 'custom'
    
    # Restrictions
    max_users = db.Column(db.Integer, default=2)  # Maximum number of users allowed
    max_doors = db.Column(db.Integer, default=1)  # Maximum number of doors allowed
    
    # Features enabled/disabled
    anomaly_detection_enabled = db.Column(db.Boolean, default=False)
    pdf_reports_enabled = db.Column(db.Boolean, default=False)
    scheduled_reports_enabled = db.Column(db.Boolean, default=False)
    api_access_enabled = db.Column(db.Boolean, default=False)
    
    # License validity
    is_active = db.Column(db.Boolean, default=True)
    activation_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.Date, nullable=True)  # None = lifetime license
    
    # Customer info
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(120))
    company_name = db.Column(db.String(200))
    
    # Support & maintenance
    support_expiration_date = db.Column(db.Date, nullable=True)
    last_validated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadata
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_key': self.license_key,
            'license_type': self.license_type,
            'max_users': self.max_users,
            'max_doors': self.max_doors,
            'anomaly_detection_enabled': self.anomaly_detection_enabled,
            'pdf_reports_enabled': self.pdf_reports_enabled,
            'scheduled_reports_enabled': self.scheduled_reports_enabled,
            'api_access_enabled': self.api_access_enabled,
            'is_active': self.is_active,
            'activation_date': self.activation_date.strftime('%Y-%m-%d %H:%M:%S') if self.activation_date else None,
            'expiration_date': self.expiration_date.strftime('%Y-%m-%d') if self.expiration_date else None,
            'support_expiration_date': self.support_expiration_date.strftime('%Y-%m-%d') if self.support_expiration_date else None,
        }
    
    def is_valid(self):
        """Check if license is currently valid"""
        if not self.is_active:
            return False
        
        if self.expiration_date:
            from datetime import date
            if date.today() > self.expiration_date:
                return False
        
        return True
    
    def get_status(self):
        """Get license status message"""
        if not self.is_active:
            return "License is inactive"
        
        if self.expiration_date:
            from datetime import date
            if date.today() > self.expiration_date:
                return "License has expired"
            
            days_remaining = (self.expiration_date - date.today()).days
            if days_remaining <= 30:
                return f"License expires in {days_remaining} days"
        
        return "Active"


# ============================================================
# 21 CFR Part 11 Compliance Models
# ============================================================

class ElectronicSignature(db.Model):
    """
    Electronic signatures for 21 CFR Part 11 compliance (§11.50, §11.100, §11.200)
    Captures user signatures for critical events with non-repudiation
    """
    __tablename__ = 'electronic_signature'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, nullable=True)  # Link to EventLog or other record
    event_type = db.Column(db.String(50), nullable=False)  # 'alarm_ack', 'config_change', 'training', etc.
    action = db.Column(db.Text, nullable=False)  # Description of what was signed
    reason = db.Column(db.Text, nullable=False)  # §11.200(a) - Meaning of signature
    signature_hash = db.Column(db.String(256), nullable=False)  # SHA-256 of username+password+timestamp
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='signatures')
    
    def __repr__(self):
        return f'<ElectronicSignature {self.id}: {self.user_id} - {self.event_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'full_name': self.user.full_name if self.user else 'Unknown',
            'event_id': self.event_id,
            'event_type': self.event_type,
            'action': self.action,
            'reason': self.reason,
            'signature_hash': self.signature_hash,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }


class TrainingModule(db.Model):
    """
    Training modules for 21 CFR Part 11 compliance (§11.10(i))
    Defines training content and requirements
    """
    __tablename__ = 'training_module'
    
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Training material content
    required_for_roles = db.Column(db.String(500))  # Comma-separated roles that must complete this
    validity_period_days = db.Column(db.Integer, default=365)  # How often retraining required
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.String(20), default='1.0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<TrainingModule {self.id}: {self.module_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'module_name': self.module_name,
            'description': self.description,
            'required_for_roles': self.required_for_roles,
            'validity_period_days': self.validity_period_days,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class TrainingRecord(db.Model):
    """
    Training completion records for 21 CFR Part 11 compliance (§11.10(i))
    Tracks user training completion with electronic signatures
    """
    __tablename__ = 'training_record'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('training_module.id'), nullable=False)
    completed_date = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime)  # When retraining is required
    signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))  # Attestation signature
    score = db.Column(db.Integer)  # If there's a quiz/test
    status = db.Column(db.String(20), default='completed')  # 'completed', 'expired', 'pending'
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='training_records')
    module = db.relationship('TrainingModule', backref='completions')
    signature = db.relationship('ElectronicSignature')
    
    def __repr__(self):
        return f'<TrainingRecord {self.id}: User {self.user_id} - Module {self.module_id}>'
    
    def is_expired(self):
        """Check if training has expired"""
        if self.expiration_date:
            return datetime.utcnow() > self.expiration_date
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'full_name': self.user.full_name if self.user else 'Unknown',
            'module_id': self.module_id,
            'module_name': self.module.module_name if self.module else 'Unknown',
            'completed_date': self.completed_date.strftime('%Y-%m-%d %H:%M:%S') if self.completed_date else None,
            'expiration_date': self.expiration_date.strftime('%Y-%m-%d %H:%M:%S') if self.expiration_date else None,
            'status': self.status,
            'is_expired': self.is_expired(),
            'score': self.score
        }


class ChangeControl(db.Model):
    """
    Change control records for 21 CFR Part 11 compliance (§11.10(k)(2))
    Documents all system changes with approval workflow
    """
    __tablename__ = 'change_control'
    
    id = db.Column(db.Integer, primary_key=True)
    change_number = db.Column(db.String(50), unique=True, nullable=False)  # CC-2025-001
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    change_type = db.Column(db.String(50))  # 'feature', 'bugfix', 'configuration', 'security'
    priority = db.Column(db.String(20))  # 'low', 'medium', 'high', 'critical'
    
    # Requestor information
    requested_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Multi-level approval workflow (5 levels)
    status = db.Column(db.String(30), default='pending_supervisor')  
    # Status values: 'pending_supervisor', 'pending_manager', 'pending_director', 'pending_admin', 
    #                'approved', 'rejected', 'implemented'
    
    # Level 1: Supervisor approval
    supervisor_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    supervisor_approved_date = db.Column(db.DateTime)
    supervisor_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Level 2: Manager approval
    manager_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    manager_approved_date = db.Column(db.DateTime)
    manager_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Level 3: Director approval
    director_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    director_approved_date = db.Column(db.DateTime)
    director_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Level 4: Admin/VP approval (final approval)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_date = db.Column(db.DateTime)
    approval_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Level 5: Implementation (by Admin/authorized personnel)
    implemented_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    implemented_date = db.Column(db.DateTime)
    implementation_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Version tracking
    version_before = db.Column(db.String(20))
    version_after = db.Column(db.String(20))
    
    # Impact assessment
    impact_assessment = db.Column(db.Text)  # Risk analysis
    affected_systems = db.Column(db.String(500))  # Comma-separated list
    rollback_plan = db.Column(db.Text)
    
    # Relationships
    requestor = db.relationship('User', foreign_keys=[requested_by])
    supervisor_approver = db.relationship('User', foreign_keys=[supervisor_approved_by])
    manager_approver = db.relationship('User', foreign_keys=[manager_approved_by])
    director_approver = db.relationship('User', foreign_keys=[director_approved_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    implementer = db.relationship('User', foreign_keys=[implemented_by])
    supervisor_signature = db.relationship('ElectronicSignature', foreign_keys=[supervisor_signature_id])
    manager_signature = db.relationship('ElectronicSignature', foreign_keys=[manager_signature_id])
    director_signature = db.relationship('ElectronicSignature', foreign_keys=[director_signature_id])
    approval_signature = db.relationship('ElectronicSignature', foreign_keys=[approval_signature_id])
    implementation_signature = db.relationship('ElectronicSignature', foreign_keys=[implementation_signature_id])
    
    def __repr__(self):
        return f'<ChangeControl {self.change_number}: {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'change_number': self.change_number,
            'title': self.title,
            'description': self.description,
            'change_type': self.change_type,
            'priority': self.priority,
            'requested_by': self.requestor.username if self.requestor else 'Unknown',
            'requested_date': self.requested_date.strftime('%Y-%m-%d %H:%M:%S') if self.requested_date else None,
            'status': self.status,
            'approved_by': self.approver.username if self.approver else None,
            'approved_date': self.approved_date.strftime('%Y-%m-%d %H:%M:%S') if self.approved_date else None,
            'implemented_date': self.implemented_date.strftime('%Y-%m-%d %H:%M:%S') if self.implemented_date else None,
            'version_before': self.version_before,
            'version_after': self.version_after
        }


class ChangeControlChecklistItem(db.Model):
    """
    Customizable checklist items for change control approval process
    Allows each company to define their own review criteria
    """
    __tablename__ = 'change_control_checklist_item'
    
    id = db.Column(db.Integer, primary_key=True)
    item_text = db.Column(db.String(200), nullable=False)  # "GMP impact assessed"
    description = db.Column(db.Text)  # Optional detailed explanation
    is_active = db.Column(db.Boolean, default=True)  # Can disable without deleting
    display_order = db.Column(db.Integer, default=0)  # Sort order on the form
    change_type = db.Column(db.String(50))  # Optional: Only show for specific types (null = show for all)
    is_required = db.Column(db.Boolean, default=False)  # Future: Could make some mandatory
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChecklistItem {self.id}: {self.item_text}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_text': self.item_text,
            'description': self.description,
            'is_active': self.is_active,
            'display_order': self.display_order,
            'change_type': self.change_type,
            'is_required': self.is_required
        }


class StandardOperatingProcedure(db.Model):
    """
    SOP management for 21 CFR Part 11 compliance
    Stores and versions standard operating procedures
    """
    __tablename__ = 'sop'
    
    id = db.Column(db.Integer, primary_key=True)
    sop_number = db.Column(db.String(50), unique=True, nullable=False)  # SOP-001
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # 'system_admin', 'validation', 'audit', 'backup', etc.
    content = db.Column(db.Text, nullable=False)  # SOP content/procedure steps
    version = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'approved', 'superseded'
    
    # Authorship
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Approval
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_date = db.Column(db.DateTime)
    approval_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Review schedule
    review_frequency_days = db.Column(db.Integer, default=365)  # Annual review
    next_review_date = db.Column(db.DateTime)
    
    # File attachment
    file_path = db.Column(db.String(500))  # Path to PDF/document
    
    # Relationships
    author = db.relationship('User', foreign_keys=[created_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    approval_signature = db.relationship('ElectronicSignature')
    
    def __repr__(self):
        return f'<SOP {self.sop_number}: {self.title} v{self.version}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sop_number': self.sop_number,
            'title': self.title,
            'category': self.category,
            'version': self.version,
            'status': self.status,
            'created_by': self.author.username if self.author else 'Unknown',
            'created_date': self.created_date.strftime('%Y-%m-%d %H:%M:%S') if self.created_date else None,
            'approved_by': self.approver.username if self.approver else None,
            'approved_date': self.approved_date.strftime('%Y-%m-%d %H:%M:%S') if self.approved_date else None,
            'next_review_date': self.next_review_date.strftime('%Y-%m-%d') if self.next_review_date else None
        }


class ValidationTest(db.Model):
    """
    Validation testing records for 21 CFR Part 11 compliance (§11.10(a))
    Documents IQ/OQ/PQ validation activities
    """
    __tablename__ = 'validation_test'
    
    id = db.Column(db.Integer, primary_key=True)
    test_number = db.Column(db.String(50), unique=True, nullable=False)  # VAL-IQ-001
    test_type = db.Column(db.String(20), nullable=False)  # 'IQ', 'OQ', 'PQ'
    test_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Equipment identification (critical for FDA compliance)
    equipment_name = db.Column(db.String(200))  # e.g., "eDOMOS Door Alarm System"
    equipment_model = db.Column(db.String(100))  # e.g., "eDOMOS-2.1-Pro"
    equipment_serial = db.Column(db.String(100))  # e.g., "SN-2024-001"
    
    # Test organization
    test_category = db.Column(db.String(50))  # 'Hardware', 'Software', 'Network', 'Security', 'Integration'
    prerequisites = db.Column(db.Text)  # What must be ready before test
    
    # Test execution
    procedure = db.Column(db.Text)  # Test steps
    expected_result = db.Column(db.Text)
    acceptance_criteria = db.Column(db.Text)  # Pass/fail criteria (CRITICAL)
    actual_result = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'pass', 'fail', 'retest'
    
    # Execution details
    executed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    executed_date = db.Column(db.DateTime)
    execution_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Review
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewed_date = db.Column(db.DateTime)
    review_signature_id = db.Column(db.Integer, db.ForeignKey('electronic_signature.id'))
    
    # Metadata
    system_version = db.Column(db.String(20))
    test_environment = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Relationships
    executor = db.relationship('User', foreign_keys=[executed_by])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    execution_signature = db.relationship('ElectronicSignature', foreign_keys=[execution_signature_id])
    review_signature = db.relationship('ElectronicSignature', foreign_keys=[review_signature_id])
    
    def __repr__(self):
        return f'<ValidationTest {self.test_number}: {self.test_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_number': self.test_number,
            'test_type': self.test_type,
            'test_name': self.test_name,
            'status': self.status,
            'executed_by': self.executor.username if self.executor else None,
            'executed_date': self.executed_date.strftime('%Y-%m-%d %H:%M:%S') if self.executed_date else None,
            'reviewed_by': self.reviewer.username if self.reviewer else None,
            'reviewed_date': self.reviewed_date.strftime('%Y-%m-%d %H:%M:%S') if self.reviewed_date else None,
            'system_version': self.system_version
        }


class ValidationDocument(db.Model):
    """
    Uploaded completed IQ/OQ/PQ PDF documents for FDA compliance tracking
    Stores metadata and approval workflow for validation documentation
    """
    __tablename__ = 'validation_document'
    
    id = db.Column(db.Integer, primary_key=True)
    document_number = db.Column(db.String(100), unique=True, nullable=False)  # VDOC-IQ-20251030-001
    document_type = db.Column(db.String(20), nullable=False)  # 'IQ', 'OQ', 'PQ'
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Server storage path
    file_size = db.Column(db.Integer)  # Bytes
    
    # Auto-captured metadata
    system_id = db.Column(db.String(100))  # Equipment serial number
    software_version = db.Column(db.String(50))  # eDOMOS version at upload time
    site_location = db.Column(db.String(200))  # Installation site
    
    # Upload tracking
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Approval workflow
    status = db.Column(db.String(20), default='pending')  # 'pending', 'submitted', 'approved', 'rejected', 'archived'
    submitted_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    # Additional metadata
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Relationships
    uploader = db.relationship('User', foreign_keys=[uploaded_by], backref='uploaded_documents')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_documents')
    
    def __repr__(self):
        return f'<ValidationDocument {self.document_number}: {self.document_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_number': self.document_number,
            'document_type': self.document_type,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'system_id': self.system_id,
            'software_version': self.software_version,
            'site_location': self.site_location,
            'uploaded_by': self.uploader.username if self.uploader else None,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None,
            'status': self.status,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None,
            'approved_by': self.approver.username if self.approver else None,
            'approved_at': self.approved_at.strftime('%Y-%m-%d %H:%M:%S') if self.approved_at else None,
            'description': self.description
        }
