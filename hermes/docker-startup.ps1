# Hermes Docker Production Startup Script

Write-Host "Starting Hermes Docker Production Environment..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Build and start the containers
Write-Host "Building and starting containers..." -ForegroundColor Yellow
docker compose up --build -d

# Wait for database to be ready
Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
docker compose exec django-web python manage.py migrate

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Yellow
docker compose exec django-web python manage.py collectstatic --noinput

# Create superuser if needed (uncomment the line below if you want to create one)
# docker compose exec django-web python manage.py createsuperuser

Write-Host "Hermes is now running at http://localhost:8000" -ForegroundColor Green
Write-Host "To stop the containers, run: docker compose down" -ForegroundColor Cyan 