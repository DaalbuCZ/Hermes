#!/bin/bash

# External PostgreSQL Database Setup Script for Hermes Production
# Usage: ./scripts/setup-external-db.sh [install|configure|create-user|test|full]

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

# Detect OS and package manager
detect_system() {
    print_header "Detecting System"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "Cannot detect OS"
        exit 1
    fi
    
    print_status "OS: $OS $VER"
    
    # Detect package manager
    if command -v apt-get >/dev/null 2>&1; then
        PKG_MANAGER="apt"
        print_status "Package manager: apt"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MANAGER="yum"
        print_status "Package manager: yum"
    elif command -v dnf >/dev/null 2>&1; then
        PKG_MANAGER="dnf"
        print_status "Package manager: dnf"
    else
        print_error "Unsupported package manager"
        exit 1
    fi
}

# Install PostgreSQL
install_postgresql() {
    print_header "Installing PostgreSQL"
    
    case $PKG_MANAGER in
        "apt")
            print_status "Updating package list..."
            sudo apt-get update
            
            print_status "Installing PostgreSQL..."
            sudo apt-get install -y postgresql postgresql-contrib postgresql-client
            
            print_status "Starting PostgreSQL service..."
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
        "yum"|"dnf")
            print_status "Installing PostgreSQL repository..."
            sudo $PKG_MANAGER install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
            
            print_status "Installing PostgreSQL..."
            sudo $PKG_MANAGER install -y postgresql17-server postgresql17-contrib postgresql17
            
            print_status "Initializing database..."
            sudo /usr/pgsql-17/bin/postgresql-17-setup initdb
            
            print_status "Starting PostgreSQL service..."
            sudo systemctl start postgresql-17
            sudo systemctl enable postgresql-17
            ;;
    esac
    
    print_status "✓ PostgreSQL installed and started"
}

# Find PostgreSQL configuration directory
find_postgresql_config() {
    local pg_version=$(psql --version | grep -oP '\d+\.\d+' | head -1)
    
    # Try different possible config directories
    local possible_dirs=(
        "/etc/postgresql/$pg_version/main"
        "/etc/postgresql/$(echo $pg_version | cut -d. -f1)/main"
        "/var/lib/pgsql/$pg_version/data"
        "/var/lib/pgsql/$(echo $pg_version | cut -d. -f1)/data"
    )
    
    for dir in "${possible_dirs[@]}"; do
        if [ -f "$dir/postgresql.conf" ]; then
            echo "$dir"
            return 0
        fi
    done
    
    # If not found, try to find it using postgres command
    local pg_config_dir=$(sudo -u postgres psql -c "SHOW config_file;" 2>/dev/null | grep -v "config_file" | grep -v "^-" | grep -v "^$" | head -1 | xargs dirname 2>/dev/null)
    
    if [ -n "$pg_config_dir" ] && [ -f "$pg_config_dir/postgresql.conf" ]; then
        echo "$pg_config_dir"
        return 0
    fi
    
    # Last resort: try common locations
    for dir in /etc/postgresql/*/main /var/lib/pgsql/*/data; do
        if [ -d "$dir" ] && [ -f "$dir/postgresql.conf" ]; then
            echo "$dir"
            return 0
        fi
    done
    
    return 1
}

# Configure PostgreSQL for external access
configure_postgresql() {
    print_header "Configuring PostgreSQL"
    
    # Find PostgreSQL configuration directory
    PG_CONF_DIR=$(find_postgresql_config)
    
    if [ -z "$PG_CONF_DIR" ]; then
        print_error "Could not find PostgreSQL configuration directory"
        print_status "Trying to find it manually..."
        
        # Try to find it using systemctl
        local service_name=$(systemctl list-units --type=service | grep postgresql | head -1 | awk '{print $1}')
        if [ -n "$service_name" ]; then
            print_status "Found PostgreSQL service: $service_name"
            local config_file=$(systemctl show "$service_name" | grep ExecStart | grep -o '/[^ ]*postgresql.conf' 2>/dev/null | head -1)
            if [ -n "$config_file" ]; then
                PG_CONF_DIR=$(dirname "$config_file")
                print_status "Found config directory via service: $PG_CONF_DIR"
            fi
        fi
        
        if [ -z "$PG_CONF_DIR" ] || [ ! -f "$PG_CONF_DIR/postgresql.conf" ]; then
            print_error "Still cannot find PostgreSQL configuration directory"
            print_status "Please check if PostgreSQL is properly installed"
            exit 1
        fi
    fi
    
    local pg_version=$(psql --version | grep -oP '\d+\.\d+' | head -1)
    print_status "PostgreSQL version: $pg_version"
    print_status "Config directory: $PG_CONF_DIR"
    
    # Backup original configuration
    if [ -f "$PG_CONF_DIR/postgresql.conf" ]; then
        sudo cp "$PG_CONF_DIR/postgresql.conf" "$PG_CONF_DIR/postgresql.conf.backup"
        print_status "✓ Configuration backed up"
    else
        print_error "postgresql.conf not found in $PG_CONF_DIR"
        exit 1
    fi
    
    # Configure postgresql.conf for external access
    print_status "Configuring postgresql.conf..."
    
    # Update listen_addresses
    if grep -q "#listen_addresses = 'localhost'" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF_DIR/postgresql.conf"
    elif grep -q "listen_addresses = 'localhost'" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF_DIR/postgresql.conf"
    else
        # Add if not present
        echo "listen_addresses = '*'" | sudo tee -a "$PG_CONF_DIR/postgresql.conf"
    fi
    
    # Update port (if needed)
    if grep -q "#port = 5432" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#port = 5432/port = 5432/" "$PG_CONF_DIR/postgresql.conf"
    fi
    
    # Configure logging
    if grep -q "#log_destination = 'stderr'" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#log_destination = 'stderr'/log_destination = 'stderr'/" "$PG_CONF_DIR/postgresql.conf"
    fi
    
    if grep -q "#logging_collector = off" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#logging_collector = off/logging_collector = on/" "$PG_CONF_DIR/postgresql.conf"
    fi
    
    if grep -q "#log_directory = 'log'" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#log_directory = 'log'/log_directory = 'log'/" "$PG_CONF_DIR/postgresql.conf"
    fi
    
    if grep -q "#log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'/log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'/" "$PG_CONF_DIR/postgresql.conf"
    fi
    
    if grep -q "#log_rotation_age = 1d" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#log_rotation_age = 1d/log_rotation_age = 1d/" "$PG_CONF_DIR/postgresql.conf"
    fi
    
    if grep -q "#log_rotation_size = 10MB" "$PG_CONF_DIR/postgresql.conf"; then
        sudo sed -i "s/#log_rotation_size = 10MB/log_rotation_size = 10MB/" "$PG_CONF_DIR/postgresql.conf"
    fi
    
    # Configure pg_hba.conf for external access
    print_status "Configuring pg_hba.conf..."
    
    # Backup pg_hba.conf
    if [ -f "$PG_CONF_DIR/pg_hba.conf" ]; then
        sudo cp "$PG_CONF_DIR/pg_hba.conf" "$PG_CONF_DIR/pg_hba.conf.backup"
    else
        print_error "pg_hba.conf not found in $PG_CONF_DIR"
        exit 1
    fi
    
    # Add external access rules (you should customize these for your security needs)
    if ! grep -q "External access for Hermes application" "$PG_CONF_DIR/pg_hba.conf"; then
        echo "# External access for Hermes application" | sudo tee -a "$PG_CONF_DIR/pg_hba.conf"
        echo "host    hermes_production    hermes_prod_user    0.0.0.0/0               md5" | sudo tee -a "$PG_CONF_DIR/pg_hba.conf"
        echo "host    hermes_production    hermes_prod_user    ::/0                    md5" | sudo tee -a "$PG_CONF_DIR/pg_hba.conf"
    fi
    
    # Restart PostgreSQL to apply changes
    print_status "Restarting PostgreSQL..."
    
    # Determine service name
    local service_name="postgresql"
    if systemctl list-units --type=service | grep -q "postgresql-17"; then
        service_name="postgresql-17"
    fi
    
    sudo systemctl restart "$service_name"
    
    print_status "✓ PostgreSQL configured for external access"
}

# Create database user and database
create_database_user() {
    print_header "Creating Database User and Database"
    
    # Get database settings from environment file
    local env_file="hermes/env.production"
    
    if [ ! -f "$env_file" ]; then
        print_warning "Production environment file not found: $env_file"
        print_status "Creating from template..."
        cp "hermes/env.example" "$env_file"
        print_warning "Please edit $env_file with your database settings before continuing"
        read -p "Press Enter after editing the file..."
    fi
    
    # Read database settings
    local db_name=""
    local db_user=""
    local db_password=""
    
    while IFS='=' read -r key value; do
        case "$key" in
            "DATABASE_NAME") db_name="$value" ;;
            "DATABASE_USERNAME") db_user="$value" ;;
            "DATABASE_PASSWORD") db_password="$value" ;;
        esac
    done < "$env_file"
    
    if [ -z "$db_name" ] || [ -z "$db_user" ] || [ -z "$db_password" ]; then
        print_error "Database settings not found in $env_file"
        print_status "Please ensure DATABASE_NAME, DATABASE_USERNAME, and DATABASE_PASSWORD are set"
        exit 1
    fi
    
    print_status "Database name: $db_name"
    print_status "Database user: $db_user"
    
    # Switch to postgres user to create database and user
    print_status "Creating database user..."
    sudo -u postgres psql << EOF
CREATE USER $db_user WITH PASSWORD '$db_password';
ALTER USER $db_user CREATEDB;
CREATE DATABASE $db_name OWNER $db_user;
GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;
\q
EOF
    
    print_status "✓ Database user and database created"
}

# Test database connection
test_database_connection() {
    print_header "Testing Database Connection"
    
    local env_file="hermes/env.production"
    
    if [ ! -f "$env_file" ]; then
        print_error "Environment file not found: $env_file"
        return 1
    fi
    
    # Read database settings
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
        print_error "Database settings not found in $env_file"
        return 1
    fi
    
    # Set environment variables for psql
    export PGUSER="$db_user"
    export PGPASSWORD="$db_password"
    export PGHOST="${db_host:-localhost}"
    export PGPORT="${db_port:-5432}"
    
    print_status "Testing connection to $db_name on $PGHOST:$PGPORT..."
    
    # Test connection
    if psql -c "SELECT version();" >/dev/null 2>&1; then
        print_status "✓ Database connection successful"
        
        # Test database access
        if psql -d "$db_name" -c "SELECT current_database();" >/dev/null 2>&1; then
            print_status "✓ Database access successful"
            return 0
        else
            print_error "Cannot access database $db_name"
            return 1
        fi
    else
        print_error "Cannot connect to PostgreSQL server"
        return 1
    fi
}

# Setup firewall rules
setup_firewall() {
    print_header "Setting up Firewall"
    
    # Check if ufw is available (Ubuntu)
    if command -v ufw >/dev/null 2>&1; then
        print_status "Configuring UFW firewall..."
        sudo ufw allow 5432/tcp
        print_status "✓ UFW rule added for PostgreSQL port 5432"
    # Check if firewalld is available (CentOS/RHEL)
    elif command -v firewall-cmd >/dev/null 2>&1; then
        print_status "Configuring firewalld..."
        sudo firewall-cmd --permanent --add-port=5432/tcp
        sudo firewall-cmd --reload
        print_status "✓ Firewalld rule added for PostgreSQL port 5432"
    else
        print_warning "No supported firewall detected. Please manually open port 5432"
    fi
}

# Show connection information
show_connection_info() {
    print_header "Database Connection Information"
    
    local env_file="hermes/env.production"
    
    if [ -f "$env_file" ]; then
        echo
        print_status "Your database is now ready for external connections:"
        echo
        echo -e "  ${CYAN}Host:${NC} $(hostname -I | awk '{print $1}')"
        echo -e "  ${CYAN}Port:${NC} 5432"
        echo -e "  ${CYAN}Database:${NC} $(grep DATABASE_NAME "$env_file" | cut -d'=' -f2)"
        echo -e "  ${CYAN}Username:${NC} $(grep DATABASE_USERNAME "$env_file" | cut -d'=' -f2)"
        echo -e "  ${CYAN}Password:${NC} [configured in $env_file]"
        echo
        print_status "Update your application's DATABASE_HOST to: $(hostname -I | awk '{print $1}')"
        echo
        print_warning "Security Notes:"
        echo "  - Consider restricting access to specific IP addresses in pg_hba.conf"
        echo "  - Use SSL connections for production deployments"
        echo "  - Regularly update PostgreSQL and monitor logs"
        echo
    fi
}

# Main execution
case "${1:-}" in
    "install")
        detect_system
        install_postgresql
        ;;
    "configure")
        configure_postgresql
        ;;
    "create-user")
        create_database_user
        ;;
    "test")
        test_database_connection
        ;;
    "firewall")
        setup_firewall
        ;;
    "full")
        print_header "Full External Database Setup"
        detect_system
        install_postgresql
        configure_postgresql
        create_database_user
        setup_firewall
        test_database_connection
        show_connection_info
        ;;
    "help"|"-h"|"--help"|"")
        print_header "External PostgreSQL Database Setup"
        echo "Usage: ./scripts/setup-external-db.sh [COMMAND]"
        echo
        echo "Commands:"
        echo -e "  ${CYAN}install${NC}      - Install PostgreSQL"
        echo -e "  ${CYAN}configure${NC}    - Configure PostgreSQL for external access"
        echo -e "  ${CYAN}create-user${NC}  - Create database user and database"
        echo -e "  ${CYAN}test${NC}         - Test database connection"
        echo -e "  ${CYAN}firewall${NC}     - Setup firewall rules"
        echo -e "  ${CYAN}full${NC}         - Run complete setup (recommended)"
        echo -e "  ${CYAN}help${NC}         - Show this help message"
        echo
        echo "Examples:"
        echo -e "  ${CYAN}./scripts/setup-external-db.sh full${NC}     # Complete setup"
        echo -e "  ${CYAN}./scripts/setup-external-db.sh install${NC}  # Install only"
        echo -e "  ${CYAN}./scripts/setup-external-db.sh test${NC}     # Test connection"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use './scripts/setup-external-db.sh help' for usage information."
        exit 1
        ;;
esac 