#!/bin/bash

# Database backup script for Linux VPS
# Usage: ./backup.sh [BackupPath] [RetentionDays]

set -e

# Default values
BACKUP_PATH="${1:-./backups}"
RETENTION_DAYS="${2:-30}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if PostgreSQL container is running
check_postgres() {
    if ! docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
        print_error "PostgreSQL container is not running. Please start the production environment first."
        exit 1
    fi
}

# Create backup directory
create_backup_dir() {
    if [ ! -d "$BACKUP_PATH" ]; then
        print_status "Creating backup directory: $BACKUP_PATH"
        mkdir -p "$BACKUP_PATH"
    fi
}

# Perform database backup
perform_backup() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_PATH/hermes_backup_$timestamp.sql"
    local compressed_file="$backup_file.gz"
    
    print_status "Creating database backup..."
    print_status "Backup file: $compressed_file"
    
    # Get database credentials from environment
    local db_name=$(grep "DATABASE_NAME=" hermes/env.production | cut -d'=' -f2)
    local db_user=$(grep "DATABASE_USERNAME=" hermes/env.production | cut -d'=' -f2)
    local db_password=$(grep "DATABASE_PASSWORD=" hermes/env.production | cut -d'=' -f2)
    
    # Perform backup using docker exec
    if docker-compose -f docker-compose.prod.yml exec -T db pg_dump \
        -U "$db_user" \
        -d "$db_name" \
        --no-password \
        --clean \
        --if-exists \
        --create \
        --verbose > "$backup_file" 2>/dev/null; then
        
        # Compress the backup
        gzip "$backup_file"
        
        # Verify the backup
        if [ -f "$compressed_file" ]; then
            local file_size=$(du -h "$compressed_file" | cut -f1)
            print_status "Backup completed successfully!"
            print_status "File: $compressed_file"
            print_status "Size: $file_size"
        else
            print_error "Backup file was not created properly."
            exit 1
        fi
    else
        print_error "Database backup failed."
        exit 1
    fi
}

# Clean up old backups
cleanup_old_backups() {
    print_status "Cleaning up backups older than $RETENTION_DAYS days..."
    
    local deleted_count=0
    while IFS= read -r -d '' file; do
        if [ -f "$file" ]; then
            rm "$file"
            deleted_count=$((deleted_count + 1))
            print_status "Deleted: $(basename "$file")"
        fi
    done < <(find "$BACKUP_PATH" -name "hermes_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -print0 2>/dev/null)
    
    if [ $deleted_count -eq 0 ]; then
        print_status "No old backups to clean up."
    else
        print_status "Cleaned up $deleted_count old backup(s)."
    fi
}

# Show backup statistics
show_statistics() {
    print_header "Backup Statistics"
    
    local total_backups=$(find "$BACKUP_PATH" -name "hermes_backup_*.sql.gz" -type f 2>/dev/null | wc -l)
    local total_size=$(find "$BACKUP_PATH" -name "hermes_backup_*.sql.gz" -type f -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
    
    print_status "Total backups: $total_backups"
    print_status "Total size: $total_size"
    
    if [ $total_backups -gt 0 ]; then
        echo
        print_status "Recent backups:"
        find "$BACKUP_PATH" -name "hermes_backup_*.sql.gz" -type f -exec ls -lh {} \; 2>/dev/null | head -5
    fi
}

# Main execution
main() {
    print_header "Database Backup Script"
    
    check_docker
    check_postgres
    create_backup_dir
    perform_backup
    cleanup_old_backups
    show_statistics
    
    print_status "Backup process completed successfully!"
}

# Run main function
main "$@" 