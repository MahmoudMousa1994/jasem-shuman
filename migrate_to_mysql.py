# MySQL Migration Script for Jasem Shuman Art Gallery
# This script helps you migrate from SQLite to MySQL

# IMPORTANT: Before running this script, make sure you have:
# 1. Installed MySQL Server on your system
# 2. Run the mysql_setup.sql script to create the database and user

import os
import subprocess
import sys
import django
from django.conf import settings

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n📋 {description}")
    print(f"🔧 Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def main():
    print("🚀 Starting MySQL Migration for Jasem Shuman Art Gallery")
    print("=" * 60)
    
    # Change to project directory
    project_dir = r"C:\Users\mahmo\Documents\jasem-shuman"
    os.chdir(project_dir)
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jasem_site.settings')
    
    # Python executable path
    python_exe = r"C:/Users/mahmo/Documents/.venv/Scripts/python.exe"
    
    # Step 1: Test MySQL connection
    print("\n🔍 Step 1: Testing MySQL connection...")
    test_command = f'{python_exe} -c "import os; os.environ.setdefault(\'DJANGO_SETTINGS_MODULE\', \'jasem_site.settings\'); import django; django.setup(); from django.db import connection; connection.ensure_connection(); print(\'MySQL connection successful!\')"'
    
    if not run_command(test_command, "Testing database connection"):
        print("\n⚠️  MySQL connection failed!")
        print("Please ensure:")
        print("1. MySQL Server is running")
        print("2. Database 'jasem_shuman_db' exists")
        print("3. MySQL root password is correct in settings.py")
        return False
    
    # Step 2: Create fresh migrations
    print("\n🔄 Step 2: Creating fresh migrations for MySQL...")
    commands = [
        "gallery",
        "store", 
        "accounts",
        "pages"
    ]
    
    for app in commands:
        if not run_command(f"{python_exe} manage.py makemigrations {app}", f"Creating migrations for {app} app"):
            print(f"⚠️  Warning: Could not create migrations for {app}")
    
    # Step 3: Apply migrations
    print("\n📦 Step 3: Applying migrations to MySQL...")
    if not run_command(f"{python_exe} manage.py migrate", "Applying all migrations to MySQL database"):
        print("❌ Migration failed!")
        return False
    
    # Step 4: Load data from SQLite backup
    print("\n📥 Step 4: Loading data from SQLite backup...")
    if os.path.exists("sqlite_backup.json"):
        if run_command(f"{python_exe} manage.py loaddata sqlite_backup.json", "Loading data from SQLite backup"):
            print("✅ Data migration completed successfully!")
        else:
            print("⚠️  Warning: Could not load all data. You may need to recreate some records manually.")
    else:
        print("⚠️  No SQLite backup found. You'll need to recreate data manually.")
    
    # Step 5: Create superuser
    print("\n👤 Step 5: Creating superuser...")
    print("You'll need to create a new superuser for the MySQL database.")
    print("Run this command manually after the script completes:")
    print(f"{python_exe} manage.py createsuperuser")
    
    print("\n🎉 MySQL migration completed!")
    print("=" * 60)
    print("Next steps:")
    print("1. Create a new superuser account")
    print("2. Test the application thoroughly")
    print("3. Verify all data migrated correctly")
    print("4. Update any backup/deployment scripts")

if __name__ == "__main__":
    main()