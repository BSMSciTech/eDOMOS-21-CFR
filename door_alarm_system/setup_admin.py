#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db
from models import User

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', is_admin=True, permissions='dashboard,settings,events')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin/admin123")
    else:
        print("✅ Admin user already exists!")
