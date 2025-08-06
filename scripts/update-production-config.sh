#!/bin/bash

# Update Production Configuration for External Database
# Usage: ./scripts/update-production-config.sh [interactive|auto]

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

# Generate secure secret key
generate_secret_key() {
    python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
}

# Get server IP address
get_server_ip() {
    hostname -I | awk '{print $1}'
}

# Interactive configuration
interactive_config() {
    print_header "Interactive Production Configuration"
    
    local env_file="hermes/env.production"
    
    # Create production environment file if it doesn't exist
    if [ ! -f "$env_file" ]; then
        print_status "Creating production environment file..."
        cp "hermes/env.example" "$env_file"
    fi
    
    print_status "Configuring production environment file: $env_file"
    echo
    
    # Get current values
    local current_secret_key=$(grep "DJANGO_SECRET_KEY=" "$env_file" | cut -d'=' -f2)
    local current_debug=$(grep "DEBUG=" "$env_file" | cut -d'=' -f2)
    local current_hosts=$(grep "DJANGO_ALLOWED_HOSTS=" "$env_file" | cut -d'=' -f2)
    local current_db_name=$(grep "DATABASE_NAME=" "$env_file" | cut -d'=' -f2)
    local current_db_user=$(grep "DATABASE_USERNAME=" "$env_file" | cut -d'=' -f2)
    local current_db_password=$(grep "DATABASE_PASSWORD=" "$env_file" | cut -d'=' -f2)
    local current_db_host=$(grep "DATABASE_HOST=" "$env_file" | cut -d'=' -f2)
    local current_db_port=$(grep "DATABASE_PORT=" "$env_file" | cut -d'=' -f2)
    
    # Django Settings
    echo -e "${CYAN}=== Django Settings ===${NC}"
    
    # Secret Key
    if [ "$current_secret_key" = "django-insecure-your-secret-key-here-change-in-production" ]; then
        print_warning "Using default secret key. Generating secure key..."
        new_secret_key=$(generate_secret_key)
        sed -i "s/DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$new_secret_key/" "$env_file"
        print_status "✓ Secret key updated"
    else
        print_status "Secret key already configured"
    fi
    
    # Debug mode
    if [ "$current_debug" = "True" ]; then
        print_warning "DEBUG is set to True. Setting to False for production..."
        sed -i "s/DEBUG=True/DEBUG=False/" "$env_file"
        print_status "✓ DEBUG set to False"
    else
        print_status "DEBUG already set to False"
    fi
    
    # Allowed hosts
    echo
    print_status "Current ALLOWED_HOSTS: $current_hosts"
    read -p "Enter allowed hosts (comma-separated, e.g., your-domain.com,www.your-domain.com): " new_hosts
    if [ -n "$new_hosts" ]; then
        sed -i "s/DJANGO_ALLOWED_HOSTS=.*/DJANGO_ALLOWED_HOSTS=$new_hosts/" "$env_file"
        print_status "✓ ALLOWED_HOSTS updated"
    fi
    
    # Database Settings
    echo
    echo -e "${CYAN}=== Database Settings ===${NC}"
    
    # Database name
    echo "Current database name: $current_db_name"
    read -p "Enter database name (or press Enter to keep current): " new_db_name
    if [ -n "$new_db_name" ]; then
        sed -i "s/DATABASE_NAME=.*/DATABASE_NAME=$new_db_name/" "$env_file"
        print_status "✓ Database name updated"
    fi
    
    # Database user
    echo "Current database user: $current_db_user"
    read -p "Enter database username (or press Enter to keep current): " new_db_user
    if [ -n "$new_db_user" ]; then
        sed -i "s/DATABASE_USERNAME=.*/DATABASE_USERNAME=$new_db_user/" "$env_file"
        print_status "✓ Database username updated"
    fi
    
    # Database password
    echo "Current database password: [hidden]"
    read -s -p "Enter database password (or press Enter to keep current): " new_db_password
    echo
    if [ -n "$new_db_password" ]; then
        sed -i "s/DATABASE_PASSWORD=.*/DATABASE_PASSWORD=$new_db_password/" "$env_file"
        print_status "✓ Database password updated"
    fi
    
    # Database host
    server_ip=$(get_server_ip)
    echo "Current database host: $current_db_host"
    echo "Server IP address: $server_ip"
    read -p "Enter database host (or press Enter to use server IP): " new_db_host
    if [ -n "$new_db_host" ]; then
        sed -i "s/DATABASE_HOST=.*/DATABASE_HOST=$new_db_host/" "$env_file"
        print_status "✓ Database host updated"
    else
        sed -i "s/DATABASE_HOST=.*/DATABASE_HOST=$server_ip/" "$env_file"
        print_status "✓ Database host set to server IP: $server_ip"
    fi
    
    # Database port
    echo "Current database port: $current_db_port"
    read -p "Enter database port (or press Enter to keep current): " new_db_port
    if [ -n "$new_db_port" ]; then
        sed -i "s/DATABASE_PORT=.*/DATABASE_PORT=$new_db_port/" "$env_file"
        print_status "✓ Database port updated"
    fi
    
    # Security Settings
    echo
    echo -e "${CYAN}=== Security Settings ===${NC}"
    
    # CSRF Trusted Origins
    if ! grep -q "CSRF_TRUSTED_ORIGINS=" "$env_file"; then
        read -p "Enter CSRF trusted origins (comma-separated HTTPS URLs): " csrf_origins
        if [ -n "$csrf_origins" ]; then
            echo "CSRF_TRUSTED_ORIGINS=$csrf_origins" >> "$env_file"
            print_status "✓ CSRF trusted origins added"
        fi
    fi
    
    # SSL Settings
    if ! grep -q "SECURE_SSL_REDIRECT=" "$env_file"; then
        echo "SECURE_SSL_REDIRECT=False" >> "$env_file"
        echo "SECURE_HSTS_SECONDS=31536000" >> "$env_file"
        echo "SECURE_HSTS_INCLUDE_SUBDOMAINS=True" >> "$env_file"
        echo "SECURE_HSTS_PRELOAD=True" >> "$env_file"
        echo "SECURE_BROWSER_XSS_FILTER=True" >> "$env_file"
        echo "SECURE_CONTENT_TYPE_NOSNIFF=True" >> "$env_file"
        echo "X_FRAME_OPTIONS=DENY" >> "$env_file"
        print_status "✓ Security settings added"
    fi
    
    print_status "✓ Production configuration updated"
}

# Automatic configuration
auto_config() {
    print_header "Automatic Production Configuration"
    
    local env_file="hermes/env.production"
    
    # Create production environment file if it doesn't exist
    if [ ! -f "$env_file" ]; then
        print_status "Creating production environment file..."
        cp "hermes/env.example" "$env_file"
    fi
    
    # Generate secure secret key
    print_status "Generating secure secret key..."
    new_secret_key=$(generate_secret_key)
    sed -i "s/DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$new_secret_key/" "$env_file"
    
    # Set production settings
    print_status "Setting production settings..."
    sed -i "s/DEBUG=True/DEBUG=False/" "$env_file"
    sed -i "s/DJANGO_LOGLEVEL=DEBUG/DJANGO_LOGLEVEL=WARNING/" "$env_file"
    
    # Set database host to server IP
    server_ip=$(get_server_ip)
    sed -i "s/DATABASE_HOST=.*/DATABASE_HOST=$server_ip/" "$env_file"
    
    # Add security settings if not present
    if ! grep -q "CSRF_TRUSTED_ORIGINS=" "$env_file"; then
        echo "" >> "$env_file"
        echo "# Security Settings" >> "$env_file"
        echo "CSRF_TRUSTED_ORIGINS=https://$server_ip" >> "$env_file"
        echo "SECURE_SSL_REDIRECT=False" >> "$env_file"
        echo "SECURE_HSTS_SECONDS=31536000" >> "$env_file"
        echo "SECURE_HSTS_INCLUDE_SUBDOMAINS=True" >> "$env_file"
        echo "SECURE_HSTS_PRELOAD=True" >> "$env_file"
        echo "SECURE_BROWSER_XSS_FILTER=True" >> "$env_file"
        echo "SECURE_CONTENT_TYPE_NOSNIFF=True" >> "$env_file"
        echo "X_FRAME_OPTIONS=DENY" >> "$env_file"
    fi
    
    print_status "✓ Automatic configuration completed"
    print_warning "Please review and customize the settings in $env_file"
}

# Show current configuration
show_config() {
    print_header "Current Production Configuration"
    
    local env_file="hermes/env.production"
    
    if [ ! -f "$env_file" ]; then
        print_error "Production environment file not found: $env_file"
        return 1
    fi
    
    echo
    print_status "Configuration file: $env_file"
    echo
    echo -e "${CYAN}=== Current Settings ===${NC}"
    
    # Show key settings
    echo "DJANGO_SECRET_KEY: $(grep "DJANGO_SECRET_KEY=" "$env_file" | cut -d'=' -f2 | cut -c1-20)..."
    echo "DEBUG: $(grep "DEBUG=" "$env_file" | cut -d'=' -f2)"
    echo "DJANGO_ALLOWED_HOSTS: $(grep "DJANGO_ALLOWED_HOSTS=" "$env_file" | cut -d'=' -f2)"
    echo "DATABASE_NAME: $(grep "DATABASE_NAME=" "$env_file" | cut -d'=' -f2)"
    echo "DATABASE_USERNAME: $(grep "DATABASE_USERNAME=" "$env_file" | cut -d'=' -f2)"
    echo "DATABASE_HOST: $(grep "DATABASE_HOST=" "$env_file" | cut -d'=' -f2)"
    echo "DATABASE_PORT: $(grep "DATABASE_PORT=" "$env_file" | cut -d'=' -f2)"
    
    if grep -q "CSRF_TRUSTED_ORIGINS=" "$env_file"; then
        echo "CSRF_TRUSTED_ORIGINS: $(grep "CSRF_TRUSTED_ORIGINS=" "$env_file" | cut -d'=' -f2)"
    fi
    
    echo
}

# Validate configuration
validate_config() {
    print_header "Validating Configuration"
    
    local env_file="hermes/env.production"
    
    if [ ! -f "$env_file" ]; then
        print_error "Production environment file not found: $env_file"
        return 1
    fi
    
    local errors=0
    
    # Check required settings
    if grep -q "DJANGO_SECRET_KEY=django-insecure-your-secret-key-here-change-in-production" "$env_file"; then
        print_error "Using default secret key - please change it"
        errors=$((errors + 1))
    fi
    
    if grep -q "DEBUG=True" "$env_file"; then
        print_error "DEBUG is set to True - should be False for production"
        errors=$((errors + 1))
    fi
    
    if grep -q "DATABASE_PASSWORD=hermes_password" "$env_file"; then
        print_error "Using default database password - please change it"
        errors=$((errors + 1))
    fi
    
    if [ $errors -eq 0 ]; then
        print_status "✓ Configuration validation passed"
        return 0
    else
        print_error "Configuration validation failed with $errors error(s)"
        return 1
    fi
}

# Main execution
case "${1:-}" in
    "interactive")
        interactive_config
        show_config
        validate_config
        ;;
    "auto")
        auto_config
        show_config
        validate_config
        ;;
    "show")
        show_config
        ;;
    "validate")
        validate_config
        ;;
    "help"|"-h"|"--help"|"")
        print_header "Production Configuration Update"
        echo "Usage: ./scripts/update-production-config.sh [COMMAND]"
        echo
        echo "Commands:"
        echo -e "  ${CYAN}interactive${NC} - Interactive configuration (recommended)"
        echo -e "  ${CYAN}auto${NC}        - Automatic configuration with defaults"
        echo -e "  ${CYAN}show${NC}        - Show current configuration"
        echo -e "  ${CYAN}validate${NC}    - Validate current configuration"
        echo -e "  ${CYAN}help${NC}        - Show this help message"
        echo
        echo "Examples:"
        echo -e "  ${CYAN}./scripts/update-production-config.sh interactive${NC}  # Interactive setup"
        echo -e "  ${CYAN}./scripts/update-production-config.sh auto${NC}         # Automatic setup"
        echo -e "  ${CYAN}./scripts/update-production-config.sh show${NC}         # Show config"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use './scripts/update-production-config.sh help' for usage information."
        exit 1
        ;;
esac 