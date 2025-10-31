#!/bin/bash
# AWS Deployment Script for Jasem Shuman Art Gallery
# Run this script on your AWS EC2 instance

echo "Starting deployment..."

# Navigate to project directory
cd ~/jasem-shuman

# Activate virtual environment
source django_env/bin/activate

# Install any new requirements
pip install -r requirements.txt

# Set environment variables for production
export DEBUG=False
export ALLOWED_HOSTS="your-domain.com,your-aws-ip-address"

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (optional)
# python manage.py createsuperuser

# Test the configuration
echo "Running Django system checks..."
python manage.py check --deploy

echo "Deployment completed!"
echo "Next steps:"
echo "1. Configure your web server (nginx/apache)"
echo "2. Set up SSL certificates"
echo "3. Configure your domain name"
echo "4. Set up proper environment variables"