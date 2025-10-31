#!/usr/bin/env python3
"""
License Key Generator for eDOMOS
Generate license keys for customers

Usage:
  python generate_license.py --type professional --customer "John Doe" --email "john@example.com"
"""

import argparse
from datetime import datetime, timedelta
from license_helper import create_license, LICENSE_TIERS


def main():
    parser = argparse.ArgumentParser(description='Generate eDOMOS License Keys')
    
    parser.add_argument('--type', 
                       choices=['starter', 'professional', 'enterprise', 'custom'],
                       default='professional',
                       help='License type')
    
    parser.add_argument('--customer', 
                       required=True,
                       help='Customer name')
    
    parser.add_argument('--email', 
                       required=True,
                       help='Customer email')
    
    parser.add_argument('--company', 
                       help='Company name')
    
    parser.add_argument('--duration-days', 
                       type=int,
                       help='License duration in days (omit for lifetime)')
    
    parser.add_argument('--support-days', 
                       type=int,
                       default=365,
                       help='Support duration in days (default: 365)')
    
    parser.add_argument('--max-users', 
                       type=int,
                       help='Custom max users (for custom type)')
    
    parser.add_argument('--max-doors', 
                       type=int,
                       help='Custom max doors (for custom type)')
    
    args = parser.parse_args()
    
    # Calculate dates
    expiration_date = None
    if args.duration_days:
        expiration_date = (datetime.now() + timedelta(days=args.duration_days)).date()
    
    support_expiration = (datetime.now() + timedelta(days=args.support_days)).date()
    
    # Custom limits
    custom_limits = {}
    if args.max_users:
        custom_limits['max_users'] = args.max_users
    if args.max_doors:
        custom_limits['max_doors'] = args.max_doors
    
    # Display configuration
    print("\n" + "="*60)
    print("eDOMOS LICENSE GENERATOR")
    print("="*60)
    
    config = LICENSE_TIERS[args.type].copy()
    if custom_limits:
        config.update(custom_limits)
    
    print(f"\nLicense Type: {args.type.upper()}")
    print(f"Customer: {args.customer}")
    print(f"Email: {args.email}")
    if args.company:
        print(f"Company: {args.company}")
    
    print(f"\n--- License Limits ---")
    print(f"Max Users: {config['max_users']}")
    print(f"Max Doors: {config['max_doors']}")
    
    print(f"\n--- Features Enabled ---")
    print(f"Anomaly Detection: {'✓' if config['anomaly_detection_enabled'] else '✗'}")
    print(f"PDF Reports: {'✓' if config['pdf_reports_enabled'] else '✗'}")
    print(f"Scheduled Reports: {'✓' if config['scheduled_reports_enabled'] else '✗'}")
    print(f"API Access: {'✓' if config['api_access_enabled'] else '✗'}")
    
    print(f"\n--- Validity ---")
    print(f"Expiration: {expiration_date.strftime('%Y-%m-%d') if expiration_date else 'LIFETIME'}")
    print(f"Support Until: {support_expiration.strftime('%Y-%m-%d')}")
    
    # Confirm
    response = input("\nGenerate this license? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    # Import app context
    from app import app, db
    
    with app.app_context():
        # Create license
        license = create_license(
            license_type=args.type,
            customer_name=args.customer,
            customer_email=args.email,
            company_name=args.company,
            expiration_date=expiration_date,
            support_expiration_date=support_expiration,
            custom_limits=custom_limits if custom_limits else None
        )
        
        print("\n" + "="*60)
        print("✅ LICENSE CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\nLICENSE KEY: {license.license_key}")
        print(f"\nProvide this key to the customer for activation.")
        print("="*60 + "\n")


if __name__ == '__main__':
    main()
