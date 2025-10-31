@echo off
echo Setting up MySQL database for Jasem Shuman Art Gallery...
echo.
echo Please enter your MySQL root password when prompted.
echo.

mysql -u root -p --port=3306 < mysql_setup.sql

echo.
echo Database setup completed!
echo.
pause