"""
MySQL Password Configuration Helper
Run this script to securely add your MySQL root password to Django settings.
"""

import os
import re

def update_mysql_password():
    settings_path = r"C:\Users\mahmo\Documents\jasem-shuman\jasem_site\settings.py"
    
    print("🔐 MySQL Password Configuration")
    print("=" * 40)
    print("This script will update your Django settings with your MySQL root password.")
    print("Your password will be stored in the settings.py file.")
    print()
    
    # Get password from user
    password = input("Enter your MySQL root password: ").strip()
    
    # Read current settings
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Replace the password line
    pattern = r"'PASSWORD': '',  # You'll need to enter your MySQL root password here"
    replacement = f"'PASSWORD': '{password}',"
    
    updated_content = re.sub(pattern, replacement, content)
    
    # Write back to file
    with open(settings_path, 'w') as f:
        f.write(updated_content)
    
    print("✅ MySQL password updated in Django settings!")
    print("You can now run the migration script.")
    print()
    print("Next steps:")
    print("1. Run: python migrate_to_mysql.py")
    print("2. Create superuser: python manage.py createsuperuser")
    print("3. Test the application: python manage.py runserver")

if __name__ == "__main__":
    update_mysql_password()