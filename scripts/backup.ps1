param(
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = ".\backups",
    
    [Parameter(Mandatory=$false)]
    [int]$RetentionDays = 30
)

Write-Host "Hermes Production Backup Script" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force
    Write-Host "Created backup directory: $BackupPath" -ForegroundColor Yellow
}

# Generate timestamp for backup filename
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFile = "$BackupPath\hermes_backup_$timestamp.sql"

Write-Host "Starting database backup..." -ForegroundColor Yellow

# Perform database backup
try {
    docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U ${env:DATABASE_USERNAME:-hermes_prod_user} ${env:DATABASE_NAME:-hermes_production} > $backupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database backup completed successfully: $backupFile" -ForegroundColor Green
        
        # Compress the backup
        $compressedFile = "$backupFile.gz"
        & gzip $backupFile
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Backup compressed: $compressedFile" -ForegroundColor Green
            Remove-Item $backupFile -ErrorAction SilentlyContinue
        }
    } else {
        Write-Host "✗ Database backup failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Error during backup: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Clean up old backups
Write-Host "Cleaning up old backups (older than $RetentionDays days)..." -ForegroundColor Yellow
$cutoffDate = (Get-Date).AddDays(-$RetentionDays)

Get-ChildItem -Path $BackupPath -Filter "*.gz" | ForEach-Object {
    if ($_.LastWriteTime -lt $cutoffDate) {
        Remove-Item $_.FullName -Force
        Write-Host "Removed old backup: $($_.Name)" -ForegroundColor Cyan
    }
}

Write-Host "`nBackup process completed!" -ForegroundColor Green
Write-Host "Backup location: $BackupPath" -ForegroundColor Cyan 