# Hermes Docker Production Setup

This guide will help you run the Hermes Django application in a production-ready Docker environment.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually included with Docker Desktop)

## Quick Start

1. **Clone the repository and navigate to the hermes directory**

   ```bash
   cd hermes
   ```

2. **Update the .env file with your production settings**

   - Change `DJANGO_SECRET_KEY` to a secure random string
   - Set `DEBUG=False` for production
   - Update `DJANGO_ALLOWED_HOSTS` with your domain

3. **Start the application using the provided script**

   ```powershell
   .\docker-startup.ps1
   ```

   Or manually:

   ```bash
   docker compose up --build -d
   ```

4. **Run migrations and collect static files**

   ```bash
   docker compose exec django-web python manage.py migrate
   docker compose exec django-web python manage.py collectstatic --noinput
   ```

5. **Create a superuser (optional)**
   ```bash
   docker compose exec django-web python manage.py createsuperuser
   ```

## Accessing the Application

- **Django Admin**: http://localhost:8000/admin/
- **Main Application**: http://localhost:8000/

## Environment Variables

The following environment variables are configured in the `.env` file:

- `DJANGO_SECRET_KEY`: Django secret key (change in production)
- `DEBUG`: Set to False for production
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_ENGINE`: Database engine (postgresql)
- `DATABASE_NAME`: Database name
- `DATABASE_USERNAME`: Database username
- `DATABASE_PASSWORD`: Database password
- `DATABASE_HOST`: Database host (db for Docker)
- `DATABASE_PORT`: Database port (5432)

## Docker Commands

### Start the application

```bash
docker compose up -d
```

### Stop the application

```bash
docker compose down
```

### View logs

```bash
docker compose logs -f django-web
```

### Access Django shell

```bash
docker compose exec django-web python manage.py shell
```

### Run management commands

```bash
docker compose exec django-web python manage.py [command]
```

## Production Considerations

1. **Security**:

   - Change the `DJANGO_SECRET_KEY` in production
   - Set `DEBUG=False`
   - Configure proper `ALLOWED_HOSTS`
   - Use HTTPS in production

2. **Database**:

   - The PostgreSQL data is persisted in a Docker volume
   - Consider backing up the database regularly

3. **Static Files**:

   - Static files are collected and served from the container
   - For production, consider using a CDN or reverse proxy

4. **Performance**:
   - The application uses Gunicorn with 3 workers
   - Adjust the number of workers based on your server resources

## Troubleshooting

### Container won't start

- Check if Docker Desktop is running
- Verify the `.env` file exists and has correct values
- Check logs: `docker compose logs django-web`

### Database connection issues

- Ensure the database container is running: `docker compose ps`
- Check database logs: `docker compose logs db`

### Static files not loading

- Run: `docker compose exec django-web python manage.py collectstatic --noinput`

## Development vs Production

For development, you can:

- Set `DEBUG=True` in the `.env` file
- Use the existing `startup.ps1` script for local development
- Use SQLite instead of PostgreSQL by changing the database settings

For production:

- Use this Docker setup
- Set `DEBUG=False`
- Use PostgreSQL (as configured)
- Configure proper logging and monitoring
