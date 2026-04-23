#!/bin/bash
# AI News Aggregator - Deploy Script
# Usage: ./scripts/deploy.sh [environment]
# Environment: development, staging, production

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-development}"

echo "======================================"
echo "  AI News Aggregator Deploy Script"
echo "======================================"
echo "Environment: $ENVIRONMENT"
echo "Project Root: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# Load environment variables
if [ -f ".env" ]; then
    echo "Loading .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Function to check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "Error: Docker Compose is not installed."
        exit 1
    fi
    
    echo "Prerequisites OK."
}

# Function to backup database
backup_database() {
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "Backing up database..."
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="backups/db_backup_${TIMESTAMP}.sql"
        mkdir -p backups
        
        docker exec ai-news-db pg_dump -U ${POSTGRES_USER:-ai_news} ${POSTGRES_DB:-ai_news} > "$BACKUP_FILE"
        echo "Database backed up to: $BACKUP_FILE"
    fi
}

# Function to build images
build_images() {
    echo "Building Docker images..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
    else
        docker-compose build
    fi
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    
    docker-compose exec backend python -m alembic upgrade head
}

# Function to start services
start_services() {
    echo "Starting services..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    else
        docker-compose up -d
    fi
}

# Function to wait for services
wait_for_services() {
    echo "Waiting for services to be healthy..."
    
    # Wait for database
    echo "Waiting for database..."
    for i in {1..30}; do
        if docker exec ai-news-db pg_isready -U ${POSTGRES_USER:-ai_news} &> /dev/null; then
            echo "Database is ready."
            break
        fi
        echo "Waiting for database... ($i/30)"
        sleep 2
    done
    
    # Wait for backend
    echo "Waiting for backend..."
    for i in {1..30}; do
        if curl -sf http://localhost:${BACKEND_PORT:-8000}/api/health &> /dev/null; then
            echo "Backend is ready."
            break
        fi
        echo "Waiting for backend... ($i/30)"
        sleep 2
    done
    
    # Wait for frontend
    echo "Waiting for frontend..."
    for i in {1..30}; do
        if curl -sf http://localhost:${FRONTEND_PORT:-3000} &> /dev/null; then
            echo "Frontend is ready."
            break
        fi
        echo "Waiting for frontend... ($i/30)"
        sleep 2
    done
}

# Function to show status
show_status() {
    echo ""
    echo "======================================"
    echo "  Deployment Complete!"
    echo "======================================"
    echo ""
    echo "Services:"
    docker-compose ps
    echo ""
    echo "URLs:"
    echo "  Frontend: http://localhost:${FRONTEND_PORT:-3000}"
    echo "  Backend:  http://localhost:${BACKEND_PORT:-8000}"
    echo "  API Docs: http://localhost:${BACKEND_PORT:-8000}/docs"
    echo ""
}

# Main deployment flow
main() {
    check_prerequisites
    backup_database
    build_images
    start_services
    wait_for_services
    show_status
}

# Parse command line arguments
case "$1" in
    build-only)
        check_prerequisites
        build_images
        ;;
    start)
        start_services
        wait_for_services
        show_status
        ;;
    stop)
        docker-compose down
        ;;
    restart)
        docker-compose restart
        wait_for_services
        show_status
        ;;
    logs)
        docker-compose logs -f "${2:-}"
        ;;
    migrate)
        run_migrations
        ;;
    *)
        main
        ;;
esac
