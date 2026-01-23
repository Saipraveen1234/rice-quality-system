# Rice Quality System - Docker Setup

This guide explains how to run the Rice Quality System backend using Docker.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

## Quick Start

### 1. Build and Start Services

From the project root directory:

```bash
docker-compose up --build
```

This will:
- Build the backend Docker image
- Start PostgreSQL database
- Start the backend server on port 3000

### 2. Access the Application

- **Backend API**: http://localhost:3000
- **Database**: localhost:5432

### 3. Stop Services

```bash
docker-compose down
```

To also remove volumes (database data):

```bash
docker-compose down -v
```

## Docker Commands

### Build only (without starting)
```bash
docker-compose build
```

### Start in detached mode (background)
```bash
docker-compose up -d
```

### View logs
```bash
docker-compose logs -f backend
```

### Restart services
```bash
docker-compose restart
```

### Check running containers
```bash
docker-compose ps
```

## Environment Variables

The backend uses these environment variables (configured in `docker-compose.yml`):

- `PORT`: Backend server port (default: 3000)
- `DB_HOST`: Database host (postgres)
- `DB_USER`: Database user (postgres)
- `DB_PASSWORD`: Database password (postgres)
- `DB_NAME`: Database name (rice_quality_db)
- `DB_DIALECT`: Database type (postgres)

## Volumes

- `postgres_data`: Persistent database storage
- `./backend/uploads`: Uploaded images (mounted from host)
- `./runs`: AI model inference results (mounted from host)

## Troubleshooting

### Port already in use
If port 3000 or 5432 is already in use, modify the ports in `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Change host port to 3001
```

### Database connection issues
Ensure PostgreSQL is healthy:

```bash
docker-compose ps
```

Check backend logs:

```bash
docker-compose logs backend
```

### Rebuild after code changes
```bash
docker-compose up --build
```

## Development Workflow

For local development with hot-reload, you can mount the source code:

Add to `docker-compose.yml` under backend service:

```yaml
volumes:
  - ./backend:/app/backend
  - ./ai:/app/ai
```

Then use nodemon in package.json for auto-restart.

## Production Deployment

For production:

1. Use environment-specific `.env` file
2. Set strong database passwords
3. Use proper secrets management
4. Configure reverse proxy (nginx)
5. Enable HTTPS
6. Set up monitoring and logging
