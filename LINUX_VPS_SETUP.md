# Linux VPS Setup Guide

This guide provides step-by-step instructions for setting up the Hermes application on a Linux VPS.

## Table of Contents

1. [VPS Requirements](#vps-requirements)
2. [Initial Server Setup](#initial-server-setup)
3. [Docker Installation](#docker-installation)
4. [Application Deployment](#application-deployment)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [Firewall Configuration](#firewall-configuration)
7. [Monitoring Setup](#monitoring-setup)
8. [Backup Configuration](#backup-configuration)
9. [Maintenance Tasks](#maintenance-tasks)

## VPS Requirements

### Minimum Specifications

- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Network**: Public IP with ports 80 and 443 open

### Recommended Specifications

- **CPU**: 4 cores
- **RAM**: 4GB
- **Storage**: 40GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Network**: Public IP with ports 80, 443, and 22 open

## Initial Server Setup

### 1. Connect to Your VPS

```bash
ssh root@your-server-ip
```

### 2. Create a Non-Root User (Security Best Practice)

```bash
# Create new user
adduser hermes
usermod -aG sudo hermes

# Switch to new user
su - hermes
```

### 3. Update System Packages

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 4. Install Essential Packages

```bash
# Ubuntu/Debian
sudo apt install -y curl wget git nano htop ufw fail2ban

# CentOS/RHEL
sudo yum install -y curl wget git nano htop firewalld fail2ban
```

### 5. Configure SSH Security

```bash
# Edit SSH configuration
sudo nano /etc/ssh/sshd_config

# Add/modify these lines:
Port 2222                    # Change default port
PermitRootLogin no           # Disable root login
PasswordAuthentication no    # Use key-based auth only
AllowUsers hermes           # Allow only specific user

# Restart SSH service
sudo systemctl restart sshd

# Test SSH connection before closing current session
ssh -p 2222 hermes@your-server-ip
```

## Docker Installation

### 1. Install Docker

```bash
# Download and run Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Log out and log back in for group changes to take effect
exit
ssh -p 2222 hermes@your-server-ip
```

### 2. Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 3. Configure Docker (Optional)

```bash
# Create Docker daemon configuration
sudo mkdir -p /etc/docker
sudo nano /etc/docker/daemon.json

# Add configuration for better performance
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}

# Restart Docker
sudo systemctl restart docker
```

## Application Deployment

### 1. Clone the Repository

```bash
# Clone your application repository
git clone <your-repo-url>
cd <project-directory>

# Make setup script executable
chmod +x setup-docker.sh
```

### 2. Run Initial Setup

```bash
# Run the setup script
./setup-docker.sh
```

### 3. Configure Environment

```bash
# Edit production environment file
nano hermes/env.production

# Update with your actual values:
DJANGO_SECRET_KEY=your-very-long-secure-secret-key
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_PASSWORD=your-secure-database-password
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 4. Deploy Application

```bash
# Start production environment
./docker-startup.sh production

# Check status
./docker-startup.sh status
```

## SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended)

#### 1. Install Certbot

```bash
# Ubuntu/Debian
sudo apt install certbot

# CentOS/RHEL
sudo yum install certbot
```

#### 2. Get SSL Certificates

```bash
# Stop Nginx temporarily (if running)
./docker-startup.sh stop

# Get certificates
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# Set proper ownership and permissions
sudo chown $USER:$USER nginx/ssl/*.pem
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem
```

#### 3. Set Up Auto-Renewal

```bash
# Create renewal script
nano renew-ssl.sh

# Add content:
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /home/hermes/project/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /home/hermes/project/nginx/ssl/key.pem
chown hermes:hermes /home/hermes/project/nginx/ssl/*.pem
chmod 644 /home/hermes/project/nginx/ssl/cert.pem
chmod 600 /home/hermes/project/nginx/ssl/key.pem
docker-compose -f /home/hermes/project/docker-compose.prod.yml restart nginx

# Make script executable
chmod +x renew-ssl.sh

# Add to crontab
sudo crontab -e

# Add line:
0 12 * * * /home/hermes/project/renew-ssl.sh
```

### Option 2: Self-Signed Certificates (Testing Only)

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

# Set permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem
```

## Firewall Configuration

### 1. Configure UFW (Ubuntu)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 2222/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### 2. Configure Firewalld (CentOS)

```bash
# Start and enable firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Allow services
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Reload firewall
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-all
```

### 3. Configure Fail2ban

```bash
# Create jail configuration
sudo nano /etc/fail2ban/jail.local

# Add content:
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 2222
logpath = /var/log/auth.log

# Start and enable fail2ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Check status
sudo fail2ban-client status
```

## Monitoring Setup

### 1. Access Monitoring Services

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Access Grafana (if needed)
# Default credentials: admin/admin
# URL: http://localhost:3000
```

### 2. Set Up System Monitoring

```bash
# Install Node Exporter for host metrics
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvf node_exporter-1.6.1.linux-amd64.tar.gz
sudo mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service
sudo nano /etc/systemd/system/node_exporter.service

# Add content:
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target

# Create user and start service
sudo useradd -rs /bin/false node_exporter
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

### 3. Configure Log Rotation

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/docker-app

# Add content:
/home/hermes/project/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 hermes hermes
}
```

## Backup Configuration

### 1. Set Up Automated Backups

```bash
# Create backup script
nano backup-daily.sh

# Add content:
#!/bin/bash
cd /home/hermes/project
./scripts/backup.sh /home/hermes/backups 30

# Make executable
chmod +x backup-daily.sh

# Add to crontab
crontab -e

# Add line:
0 2 * * * /home/hermes/project/backup-daily.sh
```

### 2. Set Up Offsite Backups (Optional)

```bash
# Install rclone for cloud storage
curl https://rclone.org/install.sh | sudo bash

# Configure rclone (follow interactive setup)
rclone config

# Create sync script
nano sync-backups.sh

# Add content:
#!/bin/bash
rclone sync /home/hermes/backups remote:hermes-backups --delete-after

# Make executable and add to crontab
chmod +x sync-backups.sh
# Add to crontab: 0 3 * * * /home/hermes/project/sync-backups.sh
```

## Maintenance Tasks

### 1. Regular System Updates

```bash
# Create update script
nano system-update.sh

# Add content:
#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
sudo apt autoclean

# Make executable and add to crontab
chmod +x system-update.sh
# Add to crontab: 0 4 * * 0 /home/hermes/project/system-update.sh
```

### 2. Docker Maintenance

```bash
# Create Docker cleanup script
nano docker-cleanup.sh

# Add content:
#!/bin/bash
docker system prune -f
docker volume prune -f
docker image prune -f

# Make executable and add to crontab
chmod +x docker-cleanup.sh
# Add to crontab: 0 5 * * 0 /home/hermes/project/docker-cleanup.sh
```

### 3. Application Updates

```bash
# Create application update script
nano app-update.sh

# Add content:
#!/bin/bash
cd /home/hermes/project
git pull origin main
./scripts/deploy.sh deploy

# Make executable
chmod +x app-update.sh
```

## Security Checklist

### Pre-Deployment

- [ ] SSH key-based authentication configured
- [ ] Root login disabled
- [ ] SSH port changed from 22
- [ ] Firewall configured
- [ ] Fail2ban installed and configured
- [ ] System packages updated

### Post-Deployment

- [ ] SSL certificates installed and working
- [ ] HTTPS redirect working
- [ ] Security headers configured
- [ ] Database passwords strong
- [ ] Django secret key secure
- [ ] Monitoring alerts configured

### Ongoing

- [ ] Regular security updates
- [ ] SSL certificate renewal automated
- [ ] Backup system tested
- [ ] Log monitoring active
- [ ] Access logs reviewed regularly

## Troubleshooting

### Common Issues

#### 1. Docker Permission Issues

```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

#### 2. Port Already in Use

```bash
# Check what's using the port
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Kill process if needed
sudo kill -9 <PID>
```

#### 3. SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

#### 4. Database Connection Issues

```bash
# Check database container
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Test connection
docker-compose -f docker-compose.prod.yml exec db psql -U hermes_prod_user -d hermes_production
```

## Useful Commands

### System Monitoring

```bash
# Check system resources
htop
free -h
df -h

# Check Docker resources
docker stats
docker system df

# Check application status
./docker-startup.sh status
```

### Log Management

```bash
# View application logs
./docker-startup.sh logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs django-web
docker-compose -f docker-compose.prod.yml logs nginx

# Follow logs in real-time
docker-compose -f docker-compose.prod.yml logs -f
```

### Backup and Recovery

```bash
# Create manual backup
./scripts/backup.sh

# List backups
ls -la backups/

# Restore from backup
./scripts/deploy.sh rollback
```

## Support Resources

- [Docker Documentation](https://docs.docker.com/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

For additional help, check the application logs and refer to the main `PRODUCTION_README.md`.
