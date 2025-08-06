#!/bin/bash

# Docker startup script for Linux VPS
# Usage: ./docker-startup.sh [dev|prod|production|stop|logs|rebuild|backup|deploy]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install it first."
        exit 1
    fi
}

# Function to check and create PostgreSQL database
check_create_database() {
    local env_file="${1:-hermes/env.production}"
    
    # Check if env file exists
    if [ ! -f "$env_file" ]; then
        print_warning "Environment file not found: $env_file"
        print_status "Creating from template..."
        cp "hermes/env.example" "$env_file"
        print_warning "Please edit $env_file with your database settings"
        return 1
    fi
    
    # Read database settings from env file
    local db_name=""
    local db_user=""
    local db_password=""
    local db_host=""
    local db_port=""
    
    while IFS='=' read -r key value; do
        case "$key" in
            "DATABASE_NAME") db_name="$value" ;;
            "DATABASE_USERNAME") db_user="$value" ;;
            "DATABASE_PASSWORD") db_password="$value" ;;
            "DATABASE_HOST") db_host="$value" ;;
            "DATABASE_PORT") db_port="$value" ;;
        esac
    done < "$env_file"
    
    if [ -z "$db_name" ] || [ -z "$db_user" ] || [ -z "$db_password" ]; then
        print_warning "Database settings not found in $env_file"
        return 1
    fi
    
    print_status "Checking PostgreSQL database connection..."
    
    # Set environment variables for psql
    export PGUSER="$db_user"
    export PGPASSWORD="$db_password"
    export PGHOST="$db_host"
    export PGPORT="${db_port:-5432}"
    
    # Test connection to PostgreSQL server
    if psql -c "SELECT 1;" >/dev/null 2>&1; then
        print_status "✓ PostgreSQL server connection successful"
        
        # Check if database exists
        if psql -c "SELECT 1 FROM pg_database WHERE datname = '$db_name';" 2>/dev/null | grep -q "1"; then
            print_status "✓ Database '$db_name' already exists"
            return 0
        else
            print_warning "Database '$db_name' does not exist. Creating..."
            
            # Create database
            if createdb "$db_name" 2>/dev/null; then
                print_status "✓ Database '$db_name' created successfully"
                return 0
            else
                print_error "Failed to create database '$db_name'"
                return 1
            fi
        fi
    else
        print_error "Cannot connect to PostgreSQL server"
        print_warning "Please ensure PostgreSQL is running and accessible"
        return 1
    fi
}

# Main script logic
case "${1:-}" in
    "dev")
        print_header "Starting Development Environment"
        check_docker
        check_docker_compose
        print_status "Starting development containers with hot reload..."
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    "prod"|"production")
        print_header "Starting Production Environment"
        check_docker
        check_docker_compose
        
        # Check and create database if needed
        if ! check_create_database "hermes/env.production"; then
            print_warning "Database setup incomplete. Please check your configuration."
            print_warning "You can still start the containers, but they may fail to connect to the database."
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_error "Aborting startup."
                exit 1
            fi
        fi
        
        # Load environment variables from env.production into current session
        print_status "Loading environment variables..."
        if [ -f "hermes/env.production" ]; then
            set -a  # automatically export all variables
            source "hermes/env.production"
            set +a  # turn off automatic export
            print_status "✓ Environment variables loaded"
        fi
        
        print_status "Starting production containers..."
        docker-compose -f docker-compose.prod.yml up --build -d
        print_status "Production environment started. Check logs with: ./docker-startup.sh logs"
        ;;
    "stop")
        print_header "Stopping All Containers"
        check_docker
        check_docker_compose
        print_status "Stopping all containers..."
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        docker-compose down 2>/dev/null || true
        print_status "All containers stopped."
        ;;
    "logs")
        print_header "Showing Container Logs"
        check_docker
        check_docker_compose
        if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
            docker-compose -f docker-compose.prod.yml logs -f
        elif docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
            docker-compose -f docker-compose.dev.yml logs -f
        else
            print_warning "No containers are running. Start them first with: ./docker-startup.sh dev or ./docker-startup.sh production"
        fi
        ;;
    "rebuild")
        print_header "Rebuilding All Containers"
        check_docker
        check_docker_compose
        print_status "Stopping existing containers..."
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
        docker-compose down 2>/dev/null || true
        print_status "Removing old images..."
        docker system prune -f
        print_status "Rebuilding containers..."
        docker-compose -f docker-compose.prod.yml build --no-cache
        print_status "Rebuild complete. Start with: ./docker-startup.sh production"
        ;;
    "backup")
        print_header "Creating Database Backup"
        check_docker
        if [ -f "./scripts/backup.sh" ]; then
            chmod +x ./scripts/backup.sh
            ./scripts/backup.sh
        else
            print_error "Backup script not found at ./scripts/backup.sh"
            exit 1
        fi
        ;;
    "deploy")
        print_header "Deploying to Production"
        check_docker
        if [ -f "./scripts/deploy.sh" ]; then
            chmod +x ./scripts/deploy.sh
            ./scripts/deploy.sh
        else
            print_error "Deploy script not found at ./scripts/deploy.sh"
            exit 1
        fi
        ;;
    "status")
        print_header "Container Status"
        check_docker
        print_status "Development containers:"
        docker-compose -f docker-compose.dev.yml ps 2>/dev/null || print_warning "No development containers found"
        echo
        print_status "Production containers:"
        docker-compose -f docker-compose.prod.yml ps 2>/dev/null || print_warning "No production containers found"
        ;;
    "help"|"-h"|"--help"|"")
        print_header "Docker Startup Script"
        echo "Usage: ./docker-startup.sh [COMMAND]"
        echo
        echo "Commands:"
        echo -e "  ${CYAN}dev${NC}         - Start development environment with hot reload"
        echo -e "  ${CYAN}production${NC}   - Start production environment"
        echo -e "  ${CYAN}stop${NC}         - Stop all containers"
        echo -e "  ${CYAN}logs${NC}         - Show container logs"
        echo -e "  ${CYAN}rebuild${NC}      - Rebuild all containers from scratch"
        echo -e "  ${CYAN}backup${NC}       - Create database backup"
        echo -e "  ${CYAN}deploy${NC}       - Deploy to production"
        echo -e "  ${CYAN}status${NC}       - Show container status"
        echo -e "  ${CYAN}help${NC}         - Show this help message"
        echo
        echo "Examples:"
        echo -e "  ${CYAN}./docker-startup.sh dev${NC}        # For development with hot reload"
        echo -e "  ${CYAN}./docker-startup.sh production${NC} # For production"
        echo -e "  ${CYAN}./docker-startup.sh stop${NC}       # To stop all containers"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use './docker-startup.sh help' for usage information."
        exit 1
        ;;
esac 