# Hermes Production Deployment Guide

This guide covers the production-ready deployment of the Hermes application with security, monitoring, and performance optimizations.

## 🚀 Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Domain name configured
- SSL certificates (recommended)
- Production server with sufficient resources

### 2. Initial Setup

```powershell
# Run the setup script
.\setup-docker.ps1

# Start production environment
.\docker-startup.ps1 production
```

## 🔧 Production Configuration

### Environment Variables

Edit `hermes/env.production` with your production settings:

```env
# Django Settings
DJANGO_SECRET_KEY=your-very-long-secure-secret-key-here
DEBUG=False
DJANGO_LOGLEVEL=WARNING
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Settings
DATABASE_ENGINE=postgresql
DATABASE_NAME=hermes_production
DATABASE_USERNAME=hermes_prod_user
DATABASE_PASSWORD=your-secure-database-password

# Security Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@your-domain.com
EMAIL_HOST_PASSWORD=your-email-password

# Redis Settings
REDIS_PASSWORD=your-secure-redis-password

# Monitoring
GRAFANA_PASSWORD=your-secure-grafana-password
```

### SSL Certificates

Place your SSL certificates in `nginx/ssl/`:

- `cert.pem` - SSL certificate
- `key.pem` - Private key

For Let's Encrypt certificates:

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

## 🏗️ Architecture

```
Internet
    ↓
Nginx Reverse Proxy (SSL Termination)
    ↓
React Frontend (Port 80/443)
    ↓ (proxies /api/* and /admin/*)
Django Backend (Port 8000)
    ↓
PostgreSQL Database (Port 5432)
Redis Cache (Port 6379)
    ↓
Prometheus Monitoring (Port 9090)
Grafana Dashboard (Port 3001)
```

## 📊 Monitoring & Observability

### Prometheus Metrics

Access Prometheus at `http://localhost:9090` to view:

- Application metrics
- Database performance
- Nginx access logs
- System resource usage

### Grafana Dashboards

Access Grafana at `http://localhost:3001`:

- Default credentials: `admin` / `your-grafana-password`
- Pre-configured dashboards for:
  - Application performance
  - Database metrics
  - System resources
  - Error rates

### Health Checks

All services include health check endpoints:

- Application: `https://your-domain.com/health/`
- API: `https://your-domain.com/api/health/`
- Database: Internal health checks
- Redis: Internal health checks

## 🔒 Security Features

### Implemented Security Measures

1. **HTTPS Enforcement**

   - SSL/TLS termination
   - HSTS headers
   - Secure cookie settings

2. **Security Headers**

   - X-Frame-Options: SAMEORIGIN
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection: 1; mode=block
   - Content-Security-Policy
   - Referrer-Policy

3. **Rate Limiting**

   - API endpoints: 10 requests/second
   - Admin login: 1 request/second
   - Burst protection

4. **Access Control**

   - Non-root containers
   - Minimal container permissions
   - Network isolation
   - Localhost-only database access

5. **Input Validation**
   - CSRF protection
   - SQL injection prevention
   - XSS protection

## 🚀 Deployment Commands

### Production Deployment

```powershell
# Full production deployment with monitoring
.\docker-startup.ps1 production

# Deploy with safety checks
.\scripts\deploy.ps1

# Check deployment status
.\scripts\deploy.ps1 status
```

### Database Management

```powershell
# Create backup
.\docker-startup.ps1 backup

# Manual backup
.\scripts\backup.ps1

# Restore from backup
.\scripts\deploy.ps1 rollback
```

### Service Management

```powershell
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart specific service
docker-compose -f docker-compose.prod.yml restart django-web

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale django-web=3
```

## 📈 Performance Optimizations

### Django Backend

- Gunicorn with gevent workers
- 4 worker processes
- Connection pooling
- Static file optimization
- Database query optimization

### React Frontend

- Nginx with gzip compression
- Static asset caching (1 year)
- Client-side routing
- Optimized bundle size

### Database

- Connection pooling
- Query optimization
- Indexed fields
- Regular maintenance

### Caching

- Redis for session storage
- Redis for application cache
- Nginx proxy caching
- Browser caching

## 🔧 Maintenance

### Regular Tasks

1. **Daily**

   - Check application logs
   - Monitor resource usage
   - Verify backup completion

2. **Weekly**

   - Review security logs
   - Update dependencies
   - Performance analysis

3. **Monthly**
   - SSL certificate renewal
   - Database maintenance
   - Security updates

### Backup Strategy

- **Automated**: Daily database backups
- **Retention**: 30 days
- **Compression**: Gzip compression
- **Location**: Local + offsite (recommended)

### Update Process

```powershell
# 1. Create backup
.\docker-startup.ps1 backup

# 2. Pull latest code
git pull origin main

# 3. Deploy with rollback capability
.\scripts\deploy.ps1 deploy

# 4. Verify deployment
.\scripts\deploy.ps1 status
```

## 🚨 Troubleshooting

### Common Issues

1. **SSL Certificate Issues**

   ```bash
   # Check certificate validity
   openssl x509 -in nginx/ssl/cert.pem -text -noout

   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

2. **Database Connection Issues**

   ```bash
   # Check database status
   docker-compose -f docker-compose.prod.yml exec db pg_isready

   # View database logs
   docker-compose -f docker-compose.prod.yml logs db
   ```

3. **Application Errors**

   ```bash
   # View application logs
   docker-compose -f docker-compose.prod.yml logs django-web

   # Check application health
   curl -f https://your-domain.com/health/
   ```

4. **Performance Issues**

   ```bash
   # Check resource usage
   docker stats

   # View Prometheus metrics
   curl http://localhost:9090/api/v1/query?query=up
   ```

### Emergency Procedures

1. **Service Down**

   ```powershell
   # Restart all services
   docker-compose -f docker-compose.prod.yml restart

   # Check service health
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **Database Issues**

   ```powershell
   # Restore from backup
   .\scripts\deploy.ps1 rollback
   ```

3. **Security Incident**

   ```powershell
   # Stop all services
   .\docker-startup.ps1 stop

   # Review logs for suspicious activity
   docker-compose -f docker-compose.prod.yml logs
   ```

## 📋 Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Database backup strategy in place
- [ ] Monitoring configured
- [ ] Security headers tested

### Post-Deployment

- [ ] Application accessible via HTTPS
- [ ] All health checks passing
- [ ] Monitoring dashboards working
- [ ] Backup system tested
- [ ] Performance benchmarks met
- [ ] Security scan completed

### Ongoing Maintenance

- [ ] Regular backups running
- [ ] SSL certificates renewed
- [ ] Security updates applied
- [ ] Performance monitored
- [ ] Logs reviewed
- [ ] Dependencies updated

## 📞 Support

For production issues:

1. Check the troubleshooting section
2. Review application logs
3. Check monitoring dashboards
4. Contact system administrator

## 🔗 Useful Links

- [Docker Documentation](https://docs.docker.com/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/)
