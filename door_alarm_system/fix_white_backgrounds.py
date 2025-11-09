#!/usr/bin/env python3
"""
Fix white backgrounds across all templates to dark theme
"""
import os
import re

# Files to fix
files_to_fix = [
    'templates/training/reports.html',
    'templates/training/modules.html',
    'templates/training/edit_module.html',
    'templates/training/complete_training.html',
    'templates/training/create_module.html',
    'templates/training/assign_training.html',
    'templates/training/module_detail.html',
    'templates/training/dashboard.html',
    'templates/validation/document_detail.html',
    'templates/validation/documents.html',
    'templates/validation/review.html',
    'templates/validation/create.html',
    'templates/validation/dashboard.html',
    'templates/validation/reports.html',
    'templates/validation/execute.html',
    'templates/validation/tests.html',
    'templates/validation/detail.html',
]

# Replacement patterns
replacements = [
    # White backgrounds to dark gradient
    (r'background:\s*white\s*;', 'background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);'),
    (r'background:\s*#fff\s*;', 'background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);'),
    (r'background:\s*#ffffff\s*;', 'background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);'),
    
    # Bootstrap bg-white class
    (r'bg-white', 'bg-dark'),
    
    # Yellow warning backgrounds to dark warning
    (r'background:\s*#fff3cd\s*;', 'background: rgba(255, 193, 7, 0.2);'),
]

def fix_file(filepath):
    """Fix white backgrounds in a single file"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    for pattern, replacement in replacements:
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            changes_made += matches
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed {filepath} - {changes_made} changes")
        return True
    else:
        print(f"ℹ️  No changes needed: {filepath}")
        return False

def main():
    print("🎨 Fixing white backgrounds to dark theme...")
    print("=" * 60)
    
    fixed_count = 0
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1
    
    print("=" * 60)
    print(f"✨ Complete! Fixed {fixed_count}/{len(files_to_fix)} files")

if __name__ == '__main__':
    main()
