"""
Migration script to add License table to the database
Run this once: python license_migration.py
"""

from app import app, db
from models import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text
from datetime import datetime

class License(db.Model):
    """Software license and restrictions"""
    id = Column(Integer, primary_key=True)
    license_key = Column(String(100), unique=True, nullable=False)
    license_type = Column(String(50), nullable=False)  # 'starter', 'professional', 'enterprise', 'custom'
    
    # Restrictions
    max_users = Column(Integer, default=2)  # Maximum number of users allowed
    max_doors = Column(Integer, default=1)  # Maximum number of doors allowed
    
    # Features enabled/disabled
    anomaly_detection_enabled = Column(Boolean, default=False)
    pdf_reports_enabled = Column(Boolean, default=False)
    scheduled_reports_enabled = Column(Boolean, default=False)
    api_access_enabled = Column(Boolean, default=False)
    
    # License validity
    is_active = Column(Boolean, default=True)
    activation_date = Column(DateTime, default=datetime.utcnow)
    expiration_date = Column(Date, nullable=True)  # None = lifetime license
    
    # Customer info
    customer_name = Column(String(200))
    customer_email = Column(String(120))
    company_name = Column(String(200))
    
    # Support & maintenance
    support_expiration_date = Column(Date, nullable=True)
    last_validated = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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


def create_license_table():
    """Create the License table"""
    with app.app_context():
        # Create the table
        db.create_all()
        print("✅ License table created successfully!")
        
        # Create a default Professional license for testing
        existing_license = License.query.first()
        if not existing_license:
            import secrets
            default_license = License(
                license_key=f"EDOMOS-PRO-{secrets.token_hex(8).upper()}",
                license_type='professional',
                max_users=10,
                max_doors=5,
                anomaly_detection_enabled=True,
                pdf_reports_enabled=True,
                scheduled_reports_enabled=True,
                api_access_enabled=False,
                is_active=True,
                expiration_date=None,  # Lifetime
                customer_name='Default Customer',
                notes='Default professional license for testing'
            )
            db.session.add(default_license)
            db.session.commit()
            print(f"✅ Default license created: {default_license.license_key}")
            print(f"   Type: Professional")
            print(f"   Max Users: {default_license.max_users}")
            print(f"   Max Doors: {default_license.max_doors}")
        else:
            print("ℹ️  License already exists, skipping default creation")


if __name__ == '__main__':
    create_license_table()
