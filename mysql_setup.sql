-- MySQL Database Setup for Jasem Shuman Art Gallery
-- Run this script in MySQL Command Line or MySQL Workbench

-- Create the database
CREATE DATABASE jasem_shuman_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a user for the application
CREATE USER 'jasem_user'@'localhost' IDENTIFIED BY 'jasem_password123';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON jasem_shuman_db.* TO 'jasem_user'@'localhost';

-- Apply the privileges
FLUSH PRIVILEGES;

-- Verify the database was created
SHOW DATABASES;

-- Verify the user was created
SELECT User, Host FROM mysql.user WHERE User = 'jasem_user';