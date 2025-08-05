# Production Deployment Guide for Linux VPS

This guide provides comprehensive instructions for deploying the Hermes application to a Linux VPS in production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Configuration](#environment-configuration)
4. [SSL Certificates](#ssl-certificates)
5. [Architecture Overview](#architecture-overview)
6. [Monitoring Setup](#monitoring-setup)
7. [Security Features](#security-features)
8. [Deployment Commands](#deployment-commands)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ or CentOS 8+ (recommended)
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: Minimum 10GB free space
- **CPU**: 2+ cores recommended
- **Network**: Public IP with ports 80 and 443 open

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl, wget, nano/vim

### Installation Commands

```bash
# Update system
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# OR
sudo yum update -y  # CentOS/RHEL

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and log back in for Docker group changes to take effect
```

## Quick Start

1. **Clone and setup**:

```bash
git clone <your-repo-url>
cd <project-directory>
chmod +x setup-docker.sh
./setup-docker.sh
```

2. **Configure environment**:

```bash
nano hermes/env.production
# Update with your domain, database credentials, and secret key
```

3. **Set up SSL certificates** (see [SSL Certificates](#ssl-certificates) section)

4. **Deploy to production**:

```bash
./docker-startup.sh production
```

5. **Check status**:

```bash
./docker-startup.sh status
```

## Environment Configuration

### Production Environment File

Edit `hermes/env.production` with your production settings:

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
DATABASE_HOST=db
DATABASE_PORT=5432

# Security Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# Static Files
STATIC_ROOT=/app/static
MEDIA_ROOT=/app/media

# Logging
DJANGO_LOG_LEVEL=WARNING
DJANGO_LOG_FILE=/app/logs/django.log
```

### Important Security Notes

- Generate a strong `DJANGO_SECRET_KEY` (at least 50 characters)
- Use strong database passwords
- Set `DEBUG=False` for production
- Configure `DJANGO_ALLOWED_HOSTS` with your actual domain
- Set `CSRF_TRUSTED_ORIGINS` with your HTTPS URLs

## SSL Certificates

### Option 1: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot  # Ubuntu/Debian
# OR
sudo yum install certbot  # CentOS/RHEL

# Get certificates
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*.pem
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/project/nginx/ssl/cert.pem && cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/project/nginx/ssl/key.pem && docker-compose -f /path/to/project/docker-compose.prod.yml restart nginx
```

### Option 2: Self-Signed (Testing Only)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem
```

### Option 3: Commercial Certificates

Place your `cert.pem` and `key.pem` files in the `nginx/ssl/` directory with proper permissions.

## Architecture Overview

```
Internet
    ↓
[Firewall/Router] (Ports 80, 443)
    ↓
[Nginx Reverse Proxy] (SSL termination, load balancing)
    ↓
[React Frontend] ←→ [Django Backend] ←→ [PostgreSQL Database]
    ↓                    ↓                    ↓
[Redis Cache]      [Gunicorn WSGI]    [Data Persistence]
    ↓                    ↓                    ↓
[Prometheus] ←→ [Grafana Dashboard] ←→ [Monitoring Data]
```

### Service Ports

- **80/443**: Nginx (public access)
- **8000**: Django (internal)
- **5173**: React dev server (development only)
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)
- **9090**: Prometheus (internal)
- **3000**: Grafana (internal)

## Monitoring Setup

### Prometheus Configuration

The monitoring stack includes:

- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization
- **Node Exporter**: Host system metrics (optional)

### Accessing Monitoring

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Access Grafana (if exposed)
# Default credentials: admin/admin
# URL: http://your-domain.com:3000 (if exposed)
```

### Custom Dashboards

1. Access Grafana at `http://localhost:3000`
2. Import dashboards from `monitoring/grafana/provisioning/dashboards/`
3. Configure data sources to point to Prometheus

## Security Features

### Network Security

- All internal services run on Docker network
- Only Nginx exposed to internet
- Firewall rules recommended for additional security

### Application Security

- HTTPS enforcement
- Security headers (HSTS, CSP, X-Frame-Options)
- CSRF protection
- Rate limiting on API endpoints
- Non-root container users

### Database Security

- PostgreSQL with strong authentication
- Network isolation
- Regular backups with encryption

### SSL/TLS Configuration

- TLS 1.2+ only
- Strong cipher suites
- HSTS headers
- Perfect Forward Secrecy

## Deployment Commands

### Basic Commands

```bash
# Start production environment
./docker-startup.sh production

# View logs
./docker-startup.sh logs

# Stop all services
./docker-startup.sh stop

# Check status
./docker-startup.sh status

# Rebuild containers
./docker-startup.sh rebuild
```

### Advanced Deployment

```bash
# Full deployment with health checks
./scripts/deploy.sh deploy

# Check deployment status
./scripts/deploy.sh status

# Rollback to previous version
./scripts/deploy.sh rollback
```

### Backup and Recovery

```bash
# Create database backup
./scripts/backup.sh

# Create backup with custom retention
./scripts/backup.sh ./backups 60  # 60 days retention

# List available backups
ls -la backups/
```

## Maintenance

### Regular Tasks

```bash
# Daily: Check service health
./docker-startup.sh status

# Weekly: Create backups
./scripts/backup.sh

# Monthly: Update containers
docker-compose -f docker-compose.prod.yml pull
./scripts/deploy.sh deploy

# Quarterly: Review logs and metrics
./docker-startup.sh logs
```

### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Update Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Log Management

```bash
# View application logs
./docker-startup.sh logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs django-web
docker-compose -f docker-compose.prod.yml logs nginx

# Rotate logs (if needed)
sudo logrotate /etc/logrotate.d/docker
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Monitor disk usage
df -h
du -sh backups/ logs/

# Check memory usage
free -h
```

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check Docker status
docker info

# Check container logs
./docker-startup.sh logs

# Check system resources
free -h
df -h
```

#### 2. Database Connection Issues

```bash
# Check database container
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Test database connection
docker-compose -f docker-compose.prod.yml exec db psql -U hermes_prod_user -d hermes_production
```

#### 3. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Check certificate permissions
ls -la nginx/ssl/

# Test SSL configuration
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

#### 4. Performance Issues

```bash
# Check resource usage
docker stats --no-stream

# Check slow queries
docker-compose -f docker-compose.prod.yml exec db psql -U hermes_prod_user -d hermes_production -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check Nginx access logs
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log
```

### Emergency Procedures

#### Complete System Restart

```bash
# Stop all services
./docker-startup.sh stop

# Restart Docker
sudo systemctl restart docker

# Start production environment
./docker-startup.sh production
```

#### Database Recovery

```bash
# Stop services
./docker-startup.sh stop

# Start database only
docker-compose -f docker-compose.prod.yml up -d db

# Restore from backup
gunzip -c backups/hermes_backup_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose -f docker-compose.prod.yml exec -T db psql -U hermes_prod_user -d hermes_production

# Start all services
./docker-startup.sh production
```

#### Emergency Rollback

```bash
# Rollback to previous deployment
./scripts/deploy.sh rollback
```

### Support and Logs

#### Useful Log Locations

- **Application logs**: `docker-compose -f docker-compose.prod.yml logs`
- **Nginx logs**: `docker-compose -f docker-compose.prod.yml logs nginx`
- **Database logs**: `docker-compose -f docker-compose.prod.yml logs db`
- **System logs**: `sudo journalctl -u docker`

#### Debugging Commands

```bash
# Check all container statuses
docker ps -a

# Check network connectivity
docker network ls
docker network inspect olymp_hermes-network

# Check volume mounts
docker volume ls
docker volume inspect olymp_postgres_data

# Execute commands in containers
docker-compose -f docker-compose.prod.yml exec django-web python manage.py shell
docker-compose -f docker-compose.prod.yml exec db psql -U hermes_prod_user -d hermes_production
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

For additional support, check the logs and refer to the troubleshooting section above.
