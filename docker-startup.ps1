param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod", "production", "stop", "logs", "rebuild", "backup", "deploy")]
    [string]$Action = "dev"
)

# Function to check and create PostgreSQL database
function Test-CreateDatabase {
    param(
        [string]$EnvFile = "hermes\env.production"
    )
    
    # Check if env file exists
    if (!(Test-Path $EnvFile)) {
        Write-Host "⚠ Environment file not found: $EnvFile" -ForegroundColor Yellow
        Write-Host "Creating from template..." -ForegroundColor Cyan
        Copy-Item "hermes\env.example" $EnvFile
        Write-Host "Please edit $EnvFile with your database settings" -ForegroundColor Yellow
        return $false
    }
    
    # Read database settings from env file
    $envContent = Get-Content $EnvFile | Where-Object { $_ -match "=" }
    $envVars = @{}
    foreach ($line in $envContent) {
        $parts = $line -split "=", 2
        if ($parts.Length -eq 2) {
            $envVars[$parts[0]] = $parts[1]
        }
    }
    
    # Extract database settings
    $dbName = $envVars["DATABASE_NAME"]
    $dbUser = $envVars["DATABASE_USERNAME"]
    $dbPassword = $envVars["DATABASE_PASSWORD"]
    $dbHost = $envVars["DATABASE_HOST"]
    $dbPort = $envVars["DATABASE_PORT"]
    
    if (!$dbName -or !$dbUser -or !$dbPassword) {
        Write-Host "⚠ Database settings not found in $EnvFile" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "Checking PostgreSQL database connection..." -ForegroundColor Cyan
    
    # Set environment variables for psql
    $env:PGUSER = $dbUser
    $env:PGPASSWORD = $dbPassword
    $env:PGHOST = $dbHost
    $env:PGPORT = $dbPort
    
    try {
        # Find psql executable
        $psqlPath = $null
        $possiblePaths = @(
            "C:\Program Files\PostgreSQL\17\bin\psql.exe",
            "C:\Program Files\PostgreSQL\16\bin\psql.exe",
            "C:\Program Files\PostgreSQL\15\bin\psql.exe",
            "C:\Program Files\PostgreSQL\14\bin\psql.exe",
            "C:\Program Files\PostgreSQL\13\bin\psql.exe"
        )
        
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                $psqlPath = $path
                break
            }
        }
        
        if (!$psqlPath) {
            Write-Host "✗ PostgreSQL client tools not found" -ForegroundColor Red
            Write-Host "Please ensure PostgreSQL is installed and psql.exe is available" -ForegroundColor Yellow
            return $false
        }
        
        Write-Host "Using PostgreSQL client: $psqlPath" -ForegroundColor Cyan
        
        # Test connection to PostgreSQL server (connect to postgres database)
        $testConnection = & $psqlPath -d postgres -c "SELECT 1;" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ PostgreSQL server connection successful" -ForegroundColor Green
            
            # Check if database exists
            $dbExists = & $psqlPath -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '$dbName';" 2>$null | Select-String "1"
            
            if ($dbExists) {
                Write-Host "✓ Database '$dbName' already exists" -ForegroundColor Green
                return $true
            } else {
                Write-Host "⚠ Database '$dbName' does not exist. Creating..." -ForegroundColor Yellow
                
                # Find createdb executable
                $createdbPath = $psqlPath -replace "psql.exe", "createdb.exe"
                if (Test-Path $createdbPath) {
                    $createResult = & $createdbPath $dbName 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "✓ Database '$dbName' created successfully" -ForegroundColor Green
                        return $true
                    } else {
                        Write-Host "✗ Failed to create database: $createResult" -ForegroundColor Red
                        return $false
                    }
                } else {
                    Write-Host "✗ createdb.exe not found at: $createdbPath" -ForegroundColor Red
                    return $false
                }
            }
        } else {
            Write-Host "✗ Cannot connect to PostgreSQL server" -ForegroundColor Red
            Write-Host "Please ensure PostgreSQL is running and accessible" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "✗ Error checking database: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please ensure PostgreSQL client tools (psql, createdb) are installed" -ForegroundColor Yellow
        return $false
    }
}

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
        
        # Check and create database if needed
        $dbReady = Test-CreateDatabase -EnvFile "hermes\env.production"
        if (!$dbReady) {
            Write-Host "⚠ Database setup incomplete. Please check your configuration." -ForegroundColor Yellow
            Write-Host "You can still start the containers, but they may fail to connect to the database." -ForegroundColor Yellow
            $continue = Read-Host "Continue anyway? (y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                Write-Host "Aborting startup." -ForegroundColor Red
                exit 1
            }
        }
        
        # Load environment variables from env.production into current session
        Write-Host "Loading environment variables..." -ForegroundColor Cyan
        if (Test-Path "hermes\env.production") {
            Get-Content "hermes\env.production" | ForEach-Object {
                if ($_ -match "^([^#][^=]+)=(.*)$") {
                    $name = $matches[1].Trim()
                    $value = $matches[2].Trim()
                    [Environment]::SetEnvironmentVariable($name, $value, "Process")
                }
            }
            Write-Host "✓ Environment variables loaded" -ForegroundColor Green
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