#!/bin/bash

# Docker setup script for Linux VPS
# Usage: ./setup-docker.sh

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

# Check if Docker is installed and running
check_docker() {
    print_header "Checking Docker Installation"
    
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed."
        print_status "Please install Docker first:"
        echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "  sudo sh get-docker.sh"
        echo "  sudo usermod -aG docker \$USER"
        echo "  # Then log out and log back in"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or you don't have permission to access it."
        print_status "Try:"
        echo "  sudo systemctl start docker"
        echo "  sudo usermod -aG docker \$USER"
        echo "  # Then log out and log back in"
        exit 1
    fi
    
    print_status "✓ Docker is installed and running"
    
    # Check Docker version
    local docker_version=$(docker --version)
    print_status "Docker version: $docker_version"
}

# Check if docker-compose is installed
check_docker_compose() {
    print_header "Checking Docker Compose"
    
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "docker-compose is not installed."
        print_status "Installing docker-compose..."
        
        # Install docker-compose
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        print_status "✓ docker-compose installed"
    else
        print_status "✓ docker-compose is already installed"
    fi
    
    # Check docker-compose version
    local compose_version=$(docker-compose --version)
    print_status "Docker Compose version: $compose_version"
}

# Setup environment file
setup_environment() {
    print_header "Setting up Environment Files"
    
    # Check if production environment file exists
    if [ ! -f "hermes/env.production" ]; then
        if [ -f "hermes/env.example" ]; then
            print_status "Creating production environment file from example..."
            cp hermes/env.example hermes/env.production
            print_warning "Please edit hermes/env.production with your production settings:"
            echo "  - Update DJANGO_SECRET_KEY"
            echo "  - Set DJANGO_ALLOWED_HOSTS to your domain"
            echo "  - Configure database credentials"
            echo "  - Set CSRF_TRUSTED_ORIGINS"
        else
            print_error "Environment example file not found: hermes/env.example"
            exit 1
        fi
    else
        print_status "✓ Production environment file already exists"
    fi
    
    # Check if development environment file exists
    if [ ! -f "hermes/.env" ]; then
        if [ -f "hermes/env.example" ]; then
            print_status "Creating development environment file from example..."
            cp hermes/env.example hermes/.env
            print_status "✓ Development environment file created"
        else
            print_warning "Development environment file not found: hermes/.env"
        fi
    else
        print_status "✓ Development environment file already exists"
    fi
}

# Setup SSL certificates (optional)
setup_ssl() {
    print_header "Setting up SSL Certificates"
    
    if [ ! -d "nginx/ssl" ]; then
        print_status "Creating SSL directory..."
        mkdir -p nginx/ssl
    fi
    
    if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
        print_warning "SSL certificates not found in nginx/ssl/"
        print_status "For production, you should:"
        echo "  1. Obtain SSL certificates (Let's Encrypt, commercial, or self-signed)"
        echo "  2. Place cert.pem and key.pem in nginx/ssl/"
        echo "  3. Set proper permissions: chmod 600 nginx/ssl/*.pem"
        echo
        print_status "For testing, you can create self-signed certificates:"
        echo "  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\"
        echo "    -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem"
    else
        print_status "✓ SSL certificates found"
        
        # Check permissions
        local cert_perms=$(stat -c %a nginx/ssl/cert.pem 2>/dev/null || stat -f %Lp nginx/ssl/cert.pem 2>/dev/null)
        local key_perms=$(stat -c %a nginx/ssl/key.pem 2>/dev/null || stat -f %Lp nginx/ssl/key.pem 2>/dev/null)
        
        if [ "$cert_perms" != "644" ] || [ "$key_perms" != "600" ]; then
            print_warning "SSL certificate permissions should be more restrictive:"
            echo "  chmod 644 nginx/ssl/cert.pem"
            echo "  chmod 600 nginx/ssl/key.pem"
        fi
    fi
}

# Make scripts executable
make_scripts_executable() {
    print_header "Setting up Scripts"
    
    local scripts=(
        "docker-startup.sh"
        "scripts/backup.sh"
        "scripts/deploy.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            print_status "✓ Made $script executable"
        else
            print_warning "Script not found: $script"
        fi
    done
}

# Check system requirements
check_system_requirements() {
    print_header "Checking System Requirements"
    
    # Check available memory
    local total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    if [ $total_mem -lt 2 ]; then
        print_warning "Low memory available: ${total_mem}GB"
        print_warning "Recommended: At least 2GB RAM for production"
    else
        print_status "✓ Sufficient memory: ${total_mem}GB"
    fi
    
    # Check available disk space
    local available_space=$(df . | awk 'NR==2 {print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    if [ $available_gb -lt 10 ]; then
        print_warning "Low disk space: ${available_gb}GB"
        print_warning "Recommended: At least 10GB free space"
    else
        print_status "✓ Sufficient disk space: ${available_gb}GB"
    fi
    
    # Check if ports are available
    local ports=(80 443 8000 5173 5432 6379 9090 3000)
    for port in "${ports[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            print_warning "Port $port is already in use"
        else
            print_status "✓ Port $port is available"
        fi
    done
}

# Show next steps
show_next_steps() {
    print_header "Setup Complete!"
    
    echo
    print_status "Next steps:"
    echo
    echo -e "  ${CYAN}1. Configure environment files:${NC}"
    echo "     nano hermes/env.production"
    echo "     nano hermes/.env"
    echo
    echo -e "  ${CYAN}2. Set up SSL certificates (for production):${NC}"
    echo "     # See nginx/ssl/README.md for instructions"
    echo
    echo -e "  ${CYAN}3. Start the application:${NC}"
    echo "     ./docker-startup.sh dev        # For development"
    echo "     ./docker-startup.sh production # For production"
    echo
    echo -e "  ${CYAN}4. Useful commands:${NC}"
    echo "     ./docker-startup.sh help       # Show all commands"
    echo "     ./docker-startup.sh logs       # View logs"
    echo "     ./docker-startup.sh stop       # Stop containers"
    echo "     ./scripts/backup.sh           # Create backup"
    echo "     ./scripts/deploy.sh deploy    # Deploy to production"
    echo
    print_status "For more information, see:"
    echo "  - DOCKER_README.md"
    echo "  - PRODUCTION_README.md"
}

# Main execution
main() {
    print_header "Docker Setup for Linux VPS"
    
    check_docker
    check_docker_compose
    setup_environment
    setup_ssl
    make_scripts_executable
    check_system_requirements
    show_next_steps
}

# Run main function
main "$@" 