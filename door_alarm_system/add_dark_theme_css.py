#!/usr/bin/env python3
"""
Add comprehensive dark theme CSS to all templates
"""
import os
import re

# Templates that need dark theme CSS enhancement
templates_to_fix = [
    'templates/training/reports.html',
    'templates/training/modules.html',
    'templates/training/dashboard.html',
    'templates/validation/dashboard.html',
    'templates/validation/tests.html',
    'templates/validation/reports.html',
    'templates/analytics.html',
]

# Dark theme CSS to add
DARK_THEME_CSS = """
/* Dark theme enhancements */
.report-section h6,
.report-section p,
.report-section strong,
.report-section td,
.report-section th,
.report-section label {
    color: #fff !important;
}

.report-section .text-muted {
    color: #aaa !important;
}

.report-section a {
    color: #667eea !important;
}

.report-section .table {
    background: transparent !important;
    color: #fff !important;
}

.report-section .table thead th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-color: rgba(138, 43, 226, 0.5) !important;
    color: #fff !important;
    font-weight: 600 !important;
    padding: 12px !important;
}

.report-section .table tbody td {
    border-color: rgba(138, 43, 226, 0.2) !important;
    color: #fff !important;
    background: transparent !important;
}

.report-section .table-hover tbody tr:hover {
    background: rgba(102, 126, 234, 0.1) !important;
}

.report-section .card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    border: 1px solid var(--border-purple) !important;
}

.report-section .card-body {
    color: #fff !important;
}

.report-section .card-body h3,
.report-section .card-body p {
    color: #fff !important;
}
"""

def add_dark_css_to_file(filepath):
    """Add dark theme CSS to a template file"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if dark theme CSS already exists
    if '/* Dark theme enhancements */' in content:
        print(f"ℹ️  Already has dark theme CSS: {filepath}")
        return False
    
    # Find the </style> tag and insert before it
    if '</style>' in content:
        content = content.replace('</style>', f'{DARK_THEME_CSS}\n</style>')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Added dark theme CSS to: {filepath}")
        return True
    else:
        print(f"⚠️  No </style> tag found in: {filepath}")
        return False

def main():
    print("🎨 Adding comprehensive dark theme CSS...")
    print("=" * 60)
    
    fixed_count = 0
    for filepath in templates_to_fix:
        if add_dark_css_to_file(filepath):
            fixed_count += 1
    
    print("=" * 60)
    print(f"✨ Complete! Enhanced {fixed_count}/{len(templates_to_fix)} files")

if __name__ == '__main__':
    main()
