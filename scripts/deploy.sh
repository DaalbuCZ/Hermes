#!/bin/bash

# Production deployment script for Linux VPS
# Usage: ./deploy.sh [deploy|status|rollback]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

# Check prerequisites
test_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_status "✓ Docker is running"
    
    # Check if docker-compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install it first."
        exit 1
    fi
    print_status "✓ docker-compose is available"
    
    # Check if environment file exists
    if [ ! -f "hermes/env.production" ]; then
        print_error "Production environment file not found: hermes/env.production"
        print_status "Please copy hermes/env.example to hermes/env.production and configure it."
        exit 1
    fi
    print_status "✓ Production environment file exists"
    
    # Check if SSL certificates exist (optional warning)
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        print_warning "SSL certificates not found in nginx/ssl/"
        print_warning "HTTPS will not work. Consider setting up SSL certificates."
    else
        print_status "✓ SSL certificates found"
    fi
    
    # Check available disk space
    local available_space=$(df . | awk 'NR==2 {print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    if [ $available_gb -lt 5 ]; then
        print_warning "Low disk space available: ${available_gb}GB"
        print_warning "Consider freeing up space before deployment."
    else
        print_status "✓ Sufficient disk space available: ${available_gb}GB"
    fi
}

# Start deployment
start_deployment() {
    print_header "Starting Production Deployment"
    
    # Stop any existing containers
    print_status "Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    # Pull latest images
    print_status "Pulling latest images..."
    docker-compose -f docker-compose.prod.yml pull
    
    # Build and start containers
    print_status "Building and starting containers..."
    docker-compose -f docker-compose.prod.yml up --build -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.prod.yml ps | grep -q "healthy"; then
            print_status "✓ All services are healthy!"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warning "Some services may not be fully healthy yet."
            print_status "Check logs with: ./docker-startup.sh logs"
            break
        fi
        
        print_status "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    # Show final status
    show_status
    print_status "Deployment completed successfully!"
}

# Start rollback
start_rollback() {
    print_header "Starting Rollback"
    
    # Check if backup exists
    local latest_backup=$(find ./backups -name "hermes_backup_*.sql.gz" -type f 2>/dev/null | sort | tail -1)
    
    if [ -z "$latest_backup" ]; then
        print_error "No backup found for rollback."
        print_status "Available backups:"
        find ./backups -name "hermes_backup_*.sql.gz" -type f 2>/dev/null | head -5 || print_warning "No backups found"
        exit 1
    fi
    
    print_status "Latest backup found: $(basename "$latest_backup")"
    print_warning "This will restore the database from backup. Continue? (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Rollback cancelled."
        exit 0
    fi
    
    # Stop containers
    print_status "Stopping containers..."
    docker-compose -f docker-compose.prod.yml down
    
    # Restore database
    print_status "Restoring database from backup..."
    docker-compose -f docker-compose.prod.yml up -d db
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Get database credentials
    local db_name=$(grep "DATABASE_NAME=" hermes/env.production | cut -d'=' -f2)
    local db_user=$(grep "DATABASE_USERNAME=" hermes/env.production | cut -d'=' -f2)
    
    # Restore backup
    gunzip -c "$latest_backup" | docker-compose -f docker-compose.prod.yml exec -T db psql -U "$db_user" -d "$db_name" 2>/dev/null || {
        print_error "Database restore failed."
        exit 1
    }
    
    # Start all services
    print_status "Starting all services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_status "Rollback completed successfully!"
    show_status
}

# Show status
show_status() {
    print_header "Service Status"
    
    print_status "Container status:"
    docker-compose -f docker-compose.prod.yml ps
    
    echo
    print_status "Service health:"
    docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    echo
    print_status "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Main execution
case "${1:-}" in
    "deploy")
        test_prerequisites
        start_deployment
        ;;
    "status")
        show_status
        ;;
    "rollback")
        test_prerequisites
        start_rollback
        ;;
    "help"|"-h"|"--help"|"")
        print_header "Production Deployment Script"
        echo "Usage: ./deploy.sh [COMMAND]"
        echo
        echo "Commands:"
        echo -e "  ${CYAN}deploy${NC}   - Deploy to production"
        echo -e "  ${CYAN}status${NC}   - Show deployment status"
        echo -e "  ${CYAN}rollback${NC} - Rollback to previous version"
        echo -e "  ${CYAN}help${NC}     - Show this help message"
        echo
        echo "Examples:"
        echo -e "  ${CYAN}./deploy.sh deploy${NC}   # Deploy to production"
        echo -e "  ${CYAN}./deploy.sh status${NC}   # Check status"
        echo -e "  ${CYAN}./deploy.sh rollback${NC} # Rollback deployment"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use './deploy.sh help' for usage information."
        exit 1
        ;;
esac 