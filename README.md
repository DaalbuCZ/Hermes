# HERMES

## **H**igh **E**fficiency **R**ecording and **M**anagement **E**valuation **S**ystem

A website to help my dance club manage the results of the physical testings done every year. The website is using Django fully, with dynamic features done by unicorn.

## Prerequisites

- Python installed
- PostgreSQL installed
- Git (so you can clone the repo)

## Steps to Set Up the Project

### 1. Clone the Repository

```bash
git clone https://github.com/DaalbuCZ/Hermes.git
cd hermes
```

### 2. Set Up the Virtual Environment

```bash
python -m venv myenv
source myenv/bin/activate  # On macOS/Linux
myenv\Scripts\activate.bat  # On Windows
```

### 3. Install Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Database Settings

Edit `hermes/settings.py` to ensure the database settings are correct for the target machine.

### 5. Migrate the Database

Run migrations:

```bash
python manage.py migrate
```

### 6. Create a Superuser

Create a superuser:

```bash
python manage.py createsuperuser
```

### 7. Start the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

### 8. Access the Site

Access your site at `http://localhost:8000`
and admin dashboard at `http://localhost:8000/admin`

### Make sure you have the database correctly setup

## Docker Deployment (Recommended)

### Quick Start with Docker

1. **Clone and setup**:

```bash
git clone https://github.com/DaalbuCZ/Hermes.git
cd hermes
chmod +x setup-docker.sh  # Linux
./setup-docker.sh         # Linux
# OR
.\setup-docker.ps1        # Windows
```

2. **Start development environment**:

```bash
./docker-startup.sh dev        # Linux
# OR
.\docker-startup.ps1 dev       # Windows
```

3. **Access the application**:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

### Full Production Environment (Recommended)

For a complete production setup with monitoring, security, and performance optimizations:

#### Linux VPS Deployment

1. **Setup**: Run `./setup-docker.sh` to configure the environment
2. **Deploy**: Use `./docker-startup.sh production` to start the full production stack
3. **Monitor**: Access Prometheus at `http://localhost:9090` and Grafana at `http://localhost:3000`
4. **Details**: See [PRODUCTION_README.md](PRODUCTION_README.md) for comprehensive instructions
5. **VPS Setup**: See [LINUX_VPS_SETUP.md](LINUX_VPS_SETUP.md) for complete server setup guide

#### Windows Development

1. **Setup**: Run `.\setup-docker.ps1` to configure the environment
2. **Deploy**: Use `.\docker-startup.ps1 production` to start the full production stack

The production environment includes:

- PostgreSQL database with Redis caching
- Nginx reverse proxy with SSL termination
- Prometheus monitoring with Grafana dashboards
- Automated backups and deployment scripts
- Security hardening and performance optimizations
- Linux VPS optimized configuration

### Docker Commands

#### Linux

```bash
./docker-startup.sh dev        # Development with hot reload
./docker-startup.sh production # Production environment
./docker-startup.sh stop       # Stop all containers
./docker-startup.sh logs       # View logs
./docker-startup.sh status     # Check status
./scripts/backup.sh           # Create backup
./scripts/deploy.sh deploy    # Deploy to production
```

#### Windows

```powershell
.\docker-startup.ps1 dev        # Development with hot reload
.\docker-startup.ps1 production # Production environment
.\docker-startup.ps1 stop       # Stop all containers
.\docker-startup.ps1 logs       # View logs
.\scripts\backup.ps1           # Create backup
.\scripts\deploy.ps1 deploy    # Deploy to production
```

For detailed Docker setup instructions, see [DOCKER_README.md](DOCKER_README.md).
