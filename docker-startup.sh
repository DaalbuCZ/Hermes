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