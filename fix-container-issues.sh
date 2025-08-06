#!/bin/bash

# Fix Container Issues Script
# This script addresses the environment variable and metrics endpoint issues

set -e

echo "🔧 Fixing container issues..."

# Function to print colored output
print_info() {
    echo -e "\033[1;34mℹ️  $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "Please run this script from the Olymp directory"
    exit 1
fi

print_info "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

print_info "Building new images with updated dependencies..."
docker-compose -f docker-compose.prod.yml build --no-cache

print_info "Starting containers with fixed configuration..."
docker-compose -f docker-compose.prod.yml up -d

print_info "Waiting for services to start..."
sleep 30

# Check service health
print_info "Checking service health..."

services=("redis" "django-web" "react-frontend" "prometheus" "grafana")
healthy=true

for service in "${services[@]}"; do
    if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
        print_success "$service is running"
    else
        print_error "$service is not healthy"
        healthy=false
    fi
done

if [ "$healthy" = true ]; then
    print_success "All services are running!"
    echo ""
    print_info "Application URLs:"
    echo "  🌐 Frontend: http://localhost (or your domain)"
    echo "  🔧 API: http://localhost:8000/api/"
    echo "  📊 Admin: http://localhost:8000/admin/"
    echo "  📈 Prometheus: http://localhost:9090"
    echo "  📊 Grafana: http://localhost:3001"
    echo ""
    print_info "To view logs:"
    echo "  docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    print_info "To check metrics endpoint:"
    echo "  curl http://localhost:8000/metrics/"
else
    print_warning "Some services may not be healthy. Check logs:"
    echo "  docker-compose -f docker-compose.prod.yml logs"
fi 