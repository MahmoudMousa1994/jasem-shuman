#!/bin/bash

# Upload static files to AWS server
echo "Uploading static files to AWS server..."

# Create the static directory on the server if it doesn't exist
ssh -o StrictHostKeyChecking=no ubuntu@51.21.218.78 "mkdir -p ~/jasem-shuman/static"

# Upload the entire static directory
scp -r static/* ubuntu@51.21.218.78:~/jasem-shuman/static/

echo "Static files uploaded successfully!"
echo "Now run: python manage.py collectstatic --noinput --clear"