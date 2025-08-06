# External Database Setup for Hermes Production

This guide will help you set up an external PostgreSQL database for your Hermes production deployment. This is useful when you want to run the database on a separate server or use a managed database service.

## Overview

The external database setup consists of two main scripts:

1. **`scripts/setup-external-db.sh`** - Sets up PostgreSQL on the database server
2. **`scripts/update-production-config.sh`** - Configures the application for external database connection

## Prerequisites

- Linux server with sudo access
- Python 3 installed (for Django secret key generation)
- Network connectivity between application and database servers

## Quick Start

### Step 1: Set up the Database Server

On your database server, run the complete setup:

```bash
# Make scripts executable
chmod +x scripts/setup-external-db.sh
chmod +x scripts/update-production-config.sh

# Run full database setup
./scripts/setup-external-db.sh full
```

This will:
- Install PostgreSQL
- Configure it for external access
- Create database user and database
- Set up firewall rules
- Test the connection

### Step 2: Configure Production Environment

On your application server, update the production configuration:

```bash
# Interactive configuration (recommended)
./scripts/update-production-config.sh interactive

# Or automatic configuration
./scripts/update-production-config.sh auto
```

### Step 3: Start Production Environment

```bash
# Start production environment
./docker-startup.sh production
```

## Detailed Setup

### Database Server Setup

#### Option 1: Complete Setup (Recommended)

```bash
./scripts/setup-external-db.sh full
```

#### Option 2: Step-by-Step Setup

```bash
# 1. Install PostgreSQL
./scripts/setup-external-db.sh install

# 2. Configure for external access
./scripts/setup-external-db.sh configure

# 3. Create database user and database
./scripts/setup-external-db.sh create-user

# 4. Set up firewall
./scripts/setup-external-db.sh firewall

# 5. Test connection
./scripts/setup-external-db.sh test
```

### Application Server Configuration

#### Interactive Configuration (Recommended)

```bash
./scripts/update-production-config.sh interactive
```

This will prompt you for:
- Allowed hosts (domains)
- Database credentials
- Security settings
- CSRF trusted origins

#### Automatic Configuration

```bash
./scripts/update-production-config.sh auto
```

This will:
- Generate a secure secret key
- Set DEBUG=False
- Set database host to server IP
- Add basic security settings

#### Validate Configuration

```bash
./scripts/update-production-config.sh validate
```

## Configuration Files

### Production Environment File

The scripts will create/update `hermes/env.production` with settings like:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secure-secret-key-here
DEBUG=False
DJANGO_LOGLEVEL=WARNING
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Settings
DATABASE_ENGINE=postgresql
DATABASE_NAME=hermes_production
DATABASE_USERNAME=hermes_prod_user
DATABASE_PASSWORD=your-secure-password
DATABASE_HOST=192.168.1.100  # Database server IP
DATABASE_PORT=5432

# Security Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
```

### PostgreSQL Configuration

The database setup script will configure:

- **postgresql.conf**: External access, logging, performance
- **pg_hba.conf**: Authentication rules for external connections
- **Firewall rules**: Allow port 5432

## Security Considerations

### Database Security

1. **Strong Passwords**: Use strong, unique passwords for database users
2. **Network Security**: Restrict database access to specific IP addresses
3. **SSL Connections**: Enable SSL for database connections in production
4. **Regular Updates**: Keep PostgreSQL updated

### Application Security

1. **Secret Key**: Generate a secure Django secret key
2. **DEBUG Mode**: Always set DEBUG=False in production
3. **Allowed Hosts**: Configure DJANGO_ALLOWED_HOSTS properly
4. **HTTPS**: Use HTTPS in production with proper SSL certificates

### Network Security

1. **Firewall**: Configure firewall to allow only necessary connections
2. **VPN**: Consider using VPN for database connections
3. **Monitoring**: Monitor database access logs

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Test database connection
./scripts/setup-external-db.sh test

# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### Configuration Issues

```bash
# Show current configuration
./scripts/update-production-config.sh show

# Validate configuration
./scripts/update-production-config.sh validate
```

#### Firewall Issues

```bash
# Check if port 5432 is open
sudo netstat -tuln | grep 5432

# Check firewall status
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-ports  # CentOS/RHEL
```

### Manual Database Setup

If the scripts don't work, you can set up the database manually:

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start and enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database user
sudo -u postgres psql
CREATE USER hermes_prod_user WITH PASSWORD 'your-secure-password';
ALTER USER hermes_prod_user CREATEDB;
CREATE DATABASE hermes_production OWNER hermes_prod_user;
GRANT ALL PRIVILEGES ON DATABASE hermes_production TO hermes_prod_user;
\q

# Configure external access
sudo nano /etc/postgresql/*/main/postgresql.conf
# Change: listen_addresses = '*'

sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add: host hermes_production hermes_prod_user 0.0.0.0/0 md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## Monitoring and Maintenance

### Database Monitoring

```bash
# Check database status
sudo systemctl status postgresql

# Monitor database logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Backup and Recovery

```bash
# Create database backup
./scripts/backup.sh

# Restore from backup
gunzip -c backup_file.sql.gz | psql -U hermes_prod_user -d hermes_production
```

### Performance Tuning

For production databases, consider:

1. **Memory Settings**: Adjust shared_buffers and work_mem
2. **Connection Pooling**: Use connection pooling for high traffic
3. **Indexing**: Monitor and optimize database indexes
4. **Vacuum**: Regular VACUUM and ANALYZE operations

## Support

For issues with the external database setup:

1. Check the troubleshooting section above
2. Review PostgreSQL logs: `/var/log/postgresql/`
3. Test network connectivity between servers
4. Verify firewall and security group settings

## Script Reference

### setup-external-db.sh Commands

- `install` - Install PostgreSQL
- `configure` - Configure for external access
- `create-user` - Create database user and database
- `test` - Test database connection
- `firewall` - Setup firewall rules
- `full` - Complete setup (recommended)

### update-production-config.sh Commands

- `interactive` - Interactive configuration (recommended)
- `auto` - Automatic configuration
- `show` - Show current configuration
- `validate` - Validate configuration 