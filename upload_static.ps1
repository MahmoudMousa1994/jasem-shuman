# Upload static files to AWS server
Write-Host "Uploading static files to AWS server..."

# Create the static directory on the server if it doesn't exist
ssh -o StrictHostKeyChecking=no ubuntu@51.21.218.78 "mkdir -p ~/jasem-shuman/static"

# Upload the entire static directory
scp -r static/* ubuntu@51.21.218.78:~/jasem-shuman/static/

Write-Host "Static files uploaded successfully!"
Write-Host "Now connect to AWS and run: python manage.py collectstatic --noinput --clear"