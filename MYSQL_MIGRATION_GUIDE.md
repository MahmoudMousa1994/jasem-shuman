# MySQL Migration Guide for Jasem Shuman Art Gallery

## Overview
This guide will help you migrate your Django project from SQLite to MySQL database.

## Prerequisites
1. **MySQL Server**: Download and install MySQL Server from https://dev.mysql.com/downloads/mysql/
2. **MySQL Workbench** (optional): GUI tool for MySQL management
3. **Backup**: Your SQLite data has been backed up to `sqlite_backup.json`

## Step-by-Step Migration Process

### Step 1: Install MySQL Server
1. Download MySQL Server installer for Windows
2. Run the installer and choose "Developer Default" setup
3. Set a root password (remember this!)
4. Complete the installation

### Step 2: Create Database and User
1. Open MySQL Command Line Client or MySQL Workbench
2. Log in with your root credentials
3. Run the script in `mysql_setup.sql`:
   ```sql
   -- Copy and paste the contents of mysql_setup.sql
   ```

### Step 3: Verify MySQL Installation
Test that MySQL is working:
```bash
mysql -u jasem_user -p jasem_shuman_db
# Enter password: jasem_password123
```

### Step 4: Run Migration Script
Execute the Python migration script:
```bash
python migrate_to_mysql.py
```

### Step 5: Manual Steps After Migration
1. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

2. **Test the Application**:
   ```bash
   python manage.py runserver
   ```

3. **Verify Data Migration**:
   - Check admin panel for all data
   - Test artwork gallery functionality
   - Verify store and cart operations
   - Test user authentication

## Database Configuration Details

### Updated Settings
Your `settings.py` now uses MySQL with these configurations:
- **Database**: jasem_shuman_db
- **User**: jasem_user
- **Password**: jasem_password123
- **Host**: localhost
- **Port**: 3306
- **Charset**: utf8mb4 (supports emojis and international characters)

### Security Considerations
For production deployment, consider:
1. Using environment variables for database credentials
2. Creating a separate database user with minimal privileges
3. Enabling SSL connections
4. Regular database backups

## Troubleshooting

### Common Issues

1. **"Access denied for user"**
   - Verify MySQL user exists and has correct password
   - Check user privileges with `SHOW GRANTS FOR 'jasem_user'@'localhost';`

2. **"Can't connect to MySQL server"**
   - Ensure MySQL service is running
   - Check if port 3306 is available
   - Verify firewall settings

3. **Migration errors**
   - Delete migration files and recreate them
   - Check for model field compatibility issues
   - Review MySQL-specific data type limitations

4. **Data loading errors**
   - Some SQLite data might not be compatible with MySQL
   - Check for foreign key constraint issues
   - Manually recreate problematic records

### Rollback to SQLite (if needed)
If you need to rollback to SQLite:
1. Restore the original settings.py database configuration
2. Your original `db.sqlite3` file is still intact
3. No data loss from the original SQLite database

## Performance Benefits with MySQL
- Better concurrent user handling
- Improved performance for large datasets
- Better support for production environments
- More robust backup and recovery options
- Better indexing capabilities

## Next Steps After Migration
1. Update any deployment scripts to use MySQL
2. Set up regular database backups
3. Monitor database performance
4. Consider MySQL optimization for production
5. Update documentation with new database requirements

## Production Deployment Considerations
When deploying to production:
- Use a managed MySQL service (AWS RDS, Google Cloud SQL, etc.)
- Set up proper backup strategies
- Configure connection pooling
- Monitor database performance
- Use environment variables for all credentials

## Support
If you encounter issues during migration:
1. Check the Django documentation for MySQL backend
2. Review MySQL error logs
3. Test database connection independently
4. Verify all dependencies are installed correctly

## Files Created During Migration
- `mysql_setup.sql` - Database setup script
- `migrate_to_mysql.py` - Migration automation script
- `sqlite_backup.json` - Backup of your SQLite data
- This guide: `MYSQL_MIGRATION_GUIDE.md`

Your original SQLite database (`db.sqlite3`) remains untouched as a backup.