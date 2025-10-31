"""
License validation and management helper functions
"""

from models import License, User, DoorSystemInfo, db
from functools import wraps
from flask import jsonify, flash, redirect, url_for
import secrets


def get_active_license():
    """Get the active license for this installation"""
    license = License.query.filter_by(is_active=True).first()
    return license


def validate_license():
    """Validate if there is an active, valid license"""
    license = get_active_license()
    if not license:
        return False, "No active license found"
    
    if not license.is_valid():
        return False, license.get_status()
    
    return True, "License is valid"


def can_add_user():
    """Check if a new user can be added based on license"""
    license = get_active_license()
    if not license:
        return False, "No active license"
    
    if not license.is_valid():
        return False, license.get_status()
    
    current_user_count = User.query.filter_by(is_active=True).count()
    
    if current_user_count >= license.max_users:
        return False, f"License limit reached: {license.max_users} users maximum (Type: {license.license_type})"
    
    return True, f"Can add {license.max_users - current_user_count} more user(s)"


def can_add_door():
    """Check if a new door can be added based on license"""
    license = get_active_license()
    if not license:
        return False, "No active license"
    
    if not license.is_valid():
        return False, license.get_status()
    
    current_door_count = DoorSystemInfo.query.filter_by(is_active=True).count()
    
    if current_door_count >= license.max_doors:
        return False, f"License limit reached: {license.max_doors} door(s) maximum (Type: {license.license_type})"
    
    return True, f"Can add {license.max_doors - current_door_count} more door(s)"


def check_feature_enabled(feature_name):
    """Check if a specific feature is enabled in the license"""
    license = get_active_license()
    if not license:
        return False
    
    if not license.is_valid():
        return False
    
    feature_map = {
        'anomaly_detection': license.anomaly_detection_enabled,
        'pdf_reports': license.pdf_reports_enabled,
        'scheduled_reports': license.scheduled_reports_enabled,
        'api_access': license.api_access_enabled
    }
    
    return feature_map.get(feature_name, False)


def get_license_info():
    """Get comprehensive license information"""
    license = get_active_license()
    if not license:
        return {
            'active': False,
            'message': 'No license found'
        }
    
    current_users = User.query.filter_by(is_active=True).count()
    current_doors = DoorSystemInfo.query.filter_by(is_active=True).count()
    
    return {
        'active': license.is_valid(),
        'license_type': license.license_type,
        'license_key': license.license_key,
        'status': license.get_status(),
        'max_users': license.max_users,
        'current_users': current_users,
        'users_remaining': max(0, license.max_users - current_users),
        'max_doors': license.max_doors,
        'current_doors': current_doors,
        'doors_remaining': max(0, license.max_doors - current_doors),
        'features': {
            'anomaly_detection': license.anomaly_detection_enabled,
            'pdf_reports': license.pdf_reports_enabled,
            'scheduled_reports': license.scheduled_reports_enabled,
            'api_access': license.api_access_enabled
        },
        'expiration_date': license.expiration_date.strftime('%Y-%m-%d') if license.expiration_date else 'Lifetime',
        'support_expiration': license.support_expiration_date.strftime('%Y-%m-%d') if license.support_expiration_date else 'N/A'
    }


def require_license(f):
    """Decorator to require valid license for route access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_valid, message = validate_license()
        if not is_valid:
            flash(f'License Error: {message}', 'danger')
            return redirect(url_for('admin'))
        return f(*args, **kwargs)
    return decorated_function


def require_feature(feature_name):
    """Decorator to require specific feature to be enabled in license"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_feature_enabled(feature_name):
                return jsonify({
                    'success': False,
                    'error': f'This feature requires a license upgrade. Feature: {feature_name}'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# License Key Generator
def generate_license_key(license_type):
    """Generate a unique license key"""
    prefix_map = {
        'starter': 'START',
        'professional': 'PRO',
        'enterprise': 'ENT',
        'custom': 'CUSTOM'
    }
    
    prefix = prefix_map.get(license_type, 'EDOMOS')
    random_part = secrets.token_hex(8).upper()
    
    return f"EDOMOS-{prefix}-{random_part}"


# Preset License Configurations
LICENSE_TIERS = {
    'starter': {
        'max_users': 2,
        'max_doors': 1,
        'anomaly_detection_enabled': False,
        'pdf_reports_enabled': False,
        'scheduled_reports_enabled': False,
        'api_access_enabled': False
    },
    'professional': {
        'max_users': 10,
        'max_doors': 5,
        'anomaly_detection_enabled': True,
        'pdf_reports_enabled': True,
        'scheduled_reports_enabled': True,
        'api_access_enabled': False
    },
    'enterprise': {
        'max_users': 50,
        'max_doors': 20,
        'anomaly_detection_enabled': True,
        'pdf_reports_enabled': True,
        'scheduled_reports_enabled': True,
        'api_access_enabled': True
    },
    'custom': {
        'max_users': 999,
        'max_doors': 999,
        'anomaly_detection_enabled': True,
        'pdf_reports_enabled': True,
        'scheduled_reports_enabled': True,
        'api_access_enabled': True
    }
}


def create_license(license_type, customer_name, customer_email, company_name=None, 
                  expiration_date=None, support_expiration_date=None, custom_limits=None):
    """Create a new license with specified parameters"""
    
    # Get preset configuration
    config = LICENSE_TIERS.get(license_type, LICENSE_TIERS['professional'])
    
    # Override with custom limits if provided
    if custom_limits:
        config.update(custom_limits)
    
    # Generate unique license key
    license_key = generate_license_key(license_type)
    
    # Create license
    new_license = License(
        license_key=license_key,
        license_type=license_type,
        max_users=config['max_users'],
        max_doors=config['max_doors'],
        anomaly_detection_enabled=config['anomaly_detection_enabled'],
        pdf_reports_enabled=config['pdf_reports_enabled'],
        scheduled_reports_enabled=config['scheduled_reports_enabled'],
        api_access_enabled=config['api_access_enabled'],
        customer_name=customer_name,
        customer_email=customer_email,
        company_name=company_name,
        expiration_date=expiration_date,
        support_expiration_date=support_expiration_date,
        is_active=True
    )
    
    db.session.add(new_license)
    db.session.commit()
    
    return new_license
