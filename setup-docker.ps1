Write-Host "Hermes Docker Setup Script" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green

# Check if .env file exists
if (Test-Path "hermes\.env") {
    Write-Host "✓ Environment file already exists" -ForegroundColor Green
} else {
    Write-Host "Creating environment file..." -ForegroundColor Yellow
    Copy-Item "hermes\env.example" "hermes\.env"
    Write-Host "✓ Environment file created from template" -ForegroundColor Green
    Write-Host "  Please review and update hermes\.env with your settings" -ForegroundColor Cyan
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "`nSetup completed! You can now run:" -ForegroundColor Green
Write-Host "  .\docker-startup.ps1 dev    # For development with hot reload" -ForegroundColor Cyan
Write-Host "  .\docker-startup.ps1 prod   # For production" -ForegroundColor Cyan
Write-Host "  .\docker-startup.ps1 stop   # To stop all containers" -ForegroundColor Cyan

Write-Host "`nFor more information, see DOCKER_README.md" -ForegroundColor Yellow 