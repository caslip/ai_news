#!/bin/bash
set -e

echo "========================================"
echo "🚀 AI News Backend - Starting..."
echo "========================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "📋 Environment Check:"
echo "   - LOG_LEVEL: ${LOG_LEVEL:-INFO}"

if [ -n "$DATABASE_URL" ]; then
    echo "   - DATABASE_URL: ${DATABASE_URL:0:30}..."
else
    echo -e "   - DATABASE_URL: ${YELLOW}NOT SET${NC} ⚠️"
fi

if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "   - OPENROUTER_API_KEY: ✅ Set"
else
    echo -e "   - OPENROUTER_API_KEY: ${YELLOW}NOT SET${NC} ⚠️"
fi

echo ""

# Database initialization
if [ -n "$DATABASE_URL" ]; then
    echo "🔧 Initializing Database..."
    python -c "
import asyncio
import sys
from app.database import engine, Base

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print('   ✅ Database tables ready')
    except Exception as e:
        print(f'   ⚠️  Database error: {e}')
        print('   ⚠️  Continuing without database...')
        sys.exit(0)

asyncio.run(init_db())
" && echo "" || echo ""
else
    echo -e "${YELLOW}⚠️  Skipping database initialization (no DATABASE_URL)${NC}"
    echo ""
fi

echo "🌟 Starting FastAPI server..."
echo "========================================"
echo ""

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
