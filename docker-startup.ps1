param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod", "stop", "logs", "rebuild")]
    [string]$Action = "dev"
)

Write-Host "Hermes Docker Management Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

switch ($Action) {
    "dev" {
        Write-Host "Starting development environment..." -ForegroundColor Yellow
        Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Cyan
        Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Django Admin will be available at: http://localhost:8000/admin" -ForegroundColor Cyan
        docker-compose -f docker-compose.dev.yml up --build
    }
    "prod" {
        Write-Host "Starting production environment..." -ForegroundColor Yellow
        Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "Django Admin will be available at: http://localhost:3000/admin" -ForegroundColor Cyan
        docker-compose up --build
    }
    "stop" {
        Write-Host "Stopping all containers..." -ForegroundColor Yellow
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        Write-Host "All containers stopped." -ForegroundColor Green
    }
    "logs" {
        Write-Host "Showing logs for all services..." -ForegroundColor Yellow
        docker-compose logs -f
    }
    "rebuild" {
        Write-Host "Rebuilding all containers..." -ForegroundColor Yellow
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        docker-compose up --build
    }
}

Write-Host "`nDocker management completed!" -ForegroundColor Green 