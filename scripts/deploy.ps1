param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("deploy", "rollback", "status")]
    [string]$Action = "deploy",
    
    [Parameter(Mandatory=$false)]
    [string]$Tag = "latest"
)

Write-Host "Hermes Production Deployment Script" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Host "✓ Docker is running" -ForegroundColor Green
    } catch {
        Write-Host "✗ Docker is not running!" -ForegroundColor Red
        exit 1
    }
    
    # Check if production env file exists
    if (!(Test-Path "hermes\env.production")) {
        Write-Host "✗ Production environment file not found!" -ForegroundColor Red
        Write-Host "Please create hermes\env.production with production settings" -ForegroundColor Yellow
        exit 1
    }
    
    # Check if SSL certificates exist
    if (!(Test-Path "nginx\ssl\cert.pem") -or !(Test-Path "nginx\ssl\key.pem")) {
        Write-Host "⚠ SSL certificates not found. Using HTTP only." -ForegroundColor Yellow
    }
    
    Write-Host "✓ Prerequisites check passed" -ForegroundColor Green
}

function Start-Deployment {
    Write-Host "Starting production deployment..." -ForegroundColor Yellow
    
    # Stop existing containers gracefully
    Write-Host "Stopping existing containers..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml down --timeout 30
    
    # Pull latest images
    Write-Host "Pulling latest images..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml pull
    
    # Build and start services
    Write-Host "Building and starting services..." -ForegroundColor Cyan
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Wait for services to be healthy
    Write-Host "Waiting for services to be healthy..." -ForegroundColor Cyan
    Start-Sleep -Seconds 30
    
    # Check service health
    $healthy = $true
    $services = @("db", "redis", "django-web", "react-frontend", "nginx")
    
    foreach ($service in $services) {
        $status = docker-compose -f docker-compose.prod.yml ps $service --format "table {{.Status}}"
        if ($status -match "Up") {
            Write-Host "✓ $service is running" -ForegroundColor Green
        } else {
            Write-Host "✗ $service is not healthy" -ForegroundColor Red
            $healthy = $false
        }
    }
    
    if ($healthy) {
        Write-Host "`n🎉 Deployment completed successfully!" -ForegroundColor Green
        Write-Host "Application is available at:" -ForegroundColor Cyan
        Write-Host "  - Frontend: https://your-domain.com" -ForegroundColor Cyan
        Write-Host "  - API: https://your-domain.com/api/" -ForegroundColor Cyan
        Write-Host "  - Admin: https://your-domain.com/admin/" -ForegroundColor Cyan
        Write-Host "  - Monitoring: http://localhost:9090 (Prometheus)" -ForegroundColor Cyan
        Write-Host "  - Monitoring: http://localhost:3001 (Grafana)" -ForegroundColor Cyan
    } else {
        Write-Host "`n⚠ Deployment completed with warnings. Check service logs." -ForegroundColor Yellow
    }
}

function Start-Rollback {
    Write-Host "Starting rollback..." -ForegroundColor Yellow
    
    # Stop current deployment
    docker-compose -f docker-compose.prod.yml down
    
    # Restore from backup if available
    $latestBackup = Get-ChildItem -Path ".\backups" -Filter "*.gz" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($latestBackup) {
        Write-Host "Restoring from backup: $($latestBackup.Name)" -ForegroundColor Cyan
        
        # Start database first
        docker-compose -f docker-compose.prod.yml up -d db
        
        # Wait for database to be ready
        Start-Sleep -Seconds 10
        
        # Restore database
        gunzip -c $latestBackup.FullName | docker-compose -f docker-compose.prod.yml exec -T db psql -U ${env:DATABASE_USERNAME:-hermes_prod_user} ${env:DATABASE_NAME:-hermes_production}
        
        Write-Host "✓ Database restored from backup" -ForegroundColor Green
    }
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    Write-Host "✓ Rollback completed" -ForegroundColor Green
}

function Show-Status {
    Write-Host "Production Status:" -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml ps
    
    Write-Host "`nService Health:" -ForegroundColor Yellow
    docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    Write-Host "`nResource Usage:" -ForegroundColor Yellow
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# Main execution
switch ($Action) {
    "deploy" {
        Test-Prerequisites
        Start-Deployment
    }
    "rollback" {
        Start-Rollback
    }
    "status" {
        Show-Status
    }
}

Write-Host "`nDeployment script completed!" -ForegroundColor Green 