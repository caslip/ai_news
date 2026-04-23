#!/bin/bash
# AI News Aggregator - Local Development Script
# Usage: ./scripts/dev.sh [command]
# Commands: start, stop, logs, db, shell, test

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "======================================"
echo "  AI News Aggregator Dev Script"
echo "======================================"

# Load environment variables
if [ -f ".env" ]; then
    echo "Loading .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Function to start development services
start_dev() {
    echo "Starting development services..."
    
    # Start PostgreSQL and Redis if not running
    if ! docker ps | grep -q "ai-news-db"; then
        echo "Starting database..."
        docker-compose up -d db redis
        echo "Waiting for database..."
        sleep 10
    fi
    
    # Run migrations
    echo "Running migrations..."
    cd backend
    python -m alembic upgrade head
    cd ..
    
    # Start backend
    echo "Starting backend..."
    cd backend
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    echo $! > ../logs/backend.pid
    cd ..
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/frontend.pid
    cd ..
    
    echo ""
    echo "Development services started!"
    echo "  Backend:  http://localhost:8000"
    echo "  Frontend: http://localhost:3000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "Logs:"
    echo "  Backend:  tail -f logs/backend.log"
    echo "  Frontend: tail -f logs/frontend.log"
}

# Function to stop development services
stop_dev() {
    echo "Stopping development services..."
    
    if [ -f logs/backend.pid ]; then
        kill $(cat logs/backend.pid) 2>/dev/null || true
        rm logs/backend.pid
    fi
    
    if [ -f logs/frontend.pid ]; then
        kill $(cat logs/frontend.pid) 2>/dev/null || true
        rm logs/frontend.pid
    fi
    
    echo "Development services stopped."
}

# Function to show logs
show_logs() {
    SERVICE="${1:-all}"
    
    mkdir -p logs
    
    case "$SERVICE" in
        backend)
            tail -f logs/backend.log
            ;;
        frontend)
            tail -f logs/frontend.log
            ;;
        all)
            echo "Backend logs (Ctrl+C to exit):"
            tail -f logs/backend.log &
            BACKEND_PID=$!
            sleep 2
            echo ""
            echo "Frontend logs (Ctrl+C to exit):"
            tail -f logs/frontend.log &
            FRONTEND_PID=$!
            trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
            wait
            ;;
        *)
            echo "Usage: $0 logs [backend|frontend|all]"
            ;;
    esac
}

# Function to open database shell
db_shell() {
    echo "Opening database shell..."
    docker exec -it ai-news-db psql -U ${POSTGRES_USER:-ai_news} -d ${POSTGRES_DB:-ai_news}
}

# Function to run backend shell
backend_shell() {
    cd backend
    python -c "import ipdb; ipdb.set_trace()" || python -c "import pdb; pdb.set_trace()"
    cd ..
}

# Function to run tests
run_tests() {
    echo "Running tests..."
    
    # Backend tests
    echo ""
    echo "Backend tests:"
    cd backend
    python -m pytest tests/ -v --tb=short
    cd ..
    
    # Frontend tests
    echo ""
    echo "Frontend tests:"
    cd frontend
    npm run test -- --run
    cd ..
}

# Main
mkdir -p logs

case "$1" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        stop_dev
        sleep 2
        start_dev
        ;;
    logs)
        show_logs "$2"
        ;;
    db)
        db_shell
        ;;
    shell)
        backend_shell
        ;;
    test)
        run_tests
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|db|shell|test}"
        ;;
esac
