#!/bin/sh

echo "========================================"
echo "AI News Frontend - Starting..."
echo "========================================"

echo ""
echo "Environment:"
echo "   - NODE_ENV: ${NODE_ENV:-production}"
echo "   - NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-http://backend:8000}"

echo ""
echo "Starting Next.js..."
echo "========================================"
echo ""

exec npm start
