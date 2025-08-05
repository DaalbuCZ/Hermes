param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod", "production", "stop", "logs", "rebuild", "backup", "deploy")]
    [string]$Action = "dev"
)

Write-Host "Hermes Docker Management Script" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

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
    "production" {
        Write-Host "Starting full production environment with monitoring..." -ForegroundColor Yellow
        Write-Host "Application will be available at: https://your-domain.com" -ForegroundColor Cyan
        Write-Host "Monitoring: http://localhost:9090 (Prometheus)" -ForegroundColor Cyan
        Write-Host "Monitoring: http://localhost:3001 (Grafana)" -ForegroundColor Cyan
        
        # Check if production env file exists
        if (!(Test-Path "hermes\env.production")) {
            Write-Host "⚠ Production environment file not found!" -ForegroundColor Yellow
            Write-Host "Creating from template..." -ForegroundColor Cyan
            Copy-Item "hermes\env.example" "hermes\env.production"
            Write-Host "Please edit hermes\env.production with your production settings" -ForegroundColor Yellow
        }
        
        docker-compose -f docker-compose.prod.yml up --build -d
    }
    "stop" {
        Write-Host "Stopping all containers..." -ForegroundColor Yellow
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        docker-compose -f docker-compose.prod.yml down
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
    "backup" {
        Write-Host "Starting database backup..." -ForegroundColor Yellow
        & ".\scripts\backup.ps1"
    }
    "deploy" {
        Write-Host "Starting production deployment..." -ForegroundColor Yellow
        & ".\scripts\deploy.ps1"
    }
}

Write-Host "`nDocker management completed!" -ForegroundColor Green 