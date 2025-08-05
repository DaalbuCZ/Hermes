# Hermes Project - Docker Setup

This project is now fully containerized with Docker, including both the Django backend and React frontend.

## Project Structure

```
Olymp/
├── docker-compose.yml          # Production Docker Compose
├── docker-compose.dev.yml      # Development Docker Compose
├── hermes/                     # Django Backend
│   ├── Dockerfile
│   ├── compose.yml            # Original Django-only compose
│   └── ...
└── OlympReact/hermes/         # React Frontend
    ├── Dockerfile             # Production build
    ├── Dockerfile.dev         # Development with hot reload
    ├── nginx.conf             # Nginx configuration
    └── ...
```

## Quick Start

### Production Environment

1. **Build and start all services:**

   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:3000/admin

### Full Production Environment (Recommended)

For production deployment with monitoring, security, and performance optimizations:

1. **Setup production environment:**

   ```powershell
   .\docker-startup.ps1 production
   ```

2. **Access the application:**
   - Application: https://your-domain.com
   - Monitoring: http://localhost:9090 (Prometheus)
   - Dashboard: http://localhost:3001 (Grafana)

**For detailed production setup, see [PRODUCTION_README.md](PRODUCTION_README.md)**

### Development Environment

1. **Start development environment with hot reloading:**

   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Access the application:**
   - Frontend (with hot reload): http://localhost:5173
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

## Services

### 1. PostgreSQL Database (`db`)

- **Port:** 5432
- **Purpose:** Main database for the Django application
- **Data Persistence:** Stored in `postgres_data` volume

### 2. Django Backend (`django-web`)

- **Port:** 8000
- **Purpose:** API server and admin interface
- **Features:**
  - Automatic migrations on startup
  - Static file collection
  - Gunicorn WSGI server (production)
  - Django development server (development)

### 3. React Frontend (`react-frontend`)

- **Port:** 3000 (production) / 5173 (development)
- **Purpose:** User interface built with React + Vite
- **Features:**
  - Nginx server (production)
  - Vite dev server with hot reload (development)
  - API proxy to Django backend
  - Client-side routing support

## Environment Variables

Create a `.env` file in the `hermes/` directory with the following variables:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_LOGLEVEL=INFO
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=hermes_db
DATABASE_USERNAME=hermes_user
DATABASE_PASSWORD=hermes_password
DATABASE_HOST=db
DATABASE_PORT=5432
```

## Docker Commands

### Production Commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f django-web
docker-compose logs -f react-frontend
```

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# Rebuild and start
docker-compose -f docker-compose.dev.yml up --build

# Stop development environment
docker-compose -f docker-compose.dev.yml down
```

### Individual Service Commands

```bash
# Run Django migrations
docker-compose exec django-web python manage.py migrate

# Create Django superuser
docker-compose exec django-web python manage.py createsuperuser

# Collect static files
docker-compose exec django-web python manage.py collectstatic

# Access Django shell
docker-compose exec django-web python manage.py shell

# Access PostgreSQL
docker-compose exec db psql -U hermes_user -d hermes_db
```

## Development Workflow

### Frontend Development

1. Start the development environment: `docker-compose -f docker-compose.dev.yml up`
2. Edit files in `OlympReact/hermes/src/`
3. Changes will automatically reload in the browser
4. API calls are proxied to the Django backend

### Backend Development

1. Start the development environment: `docker-compose -f docker-compose.dev.yml up`
2. Edit files in `hermes/`
3. Django will automatically reload on file changes
4. Database changes require running migrations manually

### Adding New Dependencies

#### Frontend (React)

1. Edit `OlympReact/hermes/package.json`
2. Rebuild the container: `docker-compose -f docker-compose.dev.yml up --build`

#### Backend (Django)

1. Edit `hermes/requirements.txt`
2. Rebuild the container: `docker-compose -f docker-compose.dev.yml up --build`

## Troubleshooting

### Common Issues

1. **Port conflicts:**

   - Change ports in `docker-compose.yml` or `docker-compose.dev.yml`
   - Check if ports 3000, 5173, 8000, or 5432 are already in use

2. **Database connection issues:**

   - Ensure the database service is running: `docker-compose ps`
   - Check database logs: `docker-compose logs db`

3. **Frontend not loading:**

   - Check if the React container is running: `docker-compose ps`
   - View frontend logs: `docker-compose logs react-frontend`

4. **API calls failing:**
   - Verify the Django backend is running: `docker-compose ps`
   - Check Django logs: `docker-compose logs django-web`

### Reset Everything

```bash
# Stop all containers and remove volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a

# Rebuild everything
docker-compose up --build
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your environment variables
2. Use a proper `DJANGO_SECRET_KEY`
3. Configure proper `DJANGO_ALLOWED_HOSTS`
4. Set up SSL/TLS certificates
5. Use external database if needed
6. Configure proper logging

## Network Architecture

```
Internet
    ↓
Nginx (React Frontend) - Port 3000
    ↓ (proxies /api/* and /admin/*)
Django Backend - Port 8000
    ↓
PostgreSQL Database - Port 5432
```

The React frontend serves as a reverse proxy, forwarding API requests to the Django backend while serving the React application for all other routes.
