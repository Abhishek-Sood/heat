#!/bin/bash
# Startup script for Render deployment
# This script starts both the MCP server and the FastAPI application

set -e

echo "🚀 Starting HEAT Clinical Assistant Backend..."

# Fix DATABASE_URL format for SQLAlchemy (Render uses postgres:// but SQLAlchemy needs postgresql+psycopg2://)
if [[ "$DATABASE_URL" == postgres://* ]]; then
    export DATABASE_URL="${DATABASE_URL/postgres:\/\//postgresql+psycopg2:\/\/}"
    echo "✅ Fixed DATABASE_URL format for SQLAlchemy"
fi

# Run database migrations
echo "📦 Running database migrations..."
cd /app
alembic upgrade head || echo "⚠️ Migrations may have already been applied"

# Setup RAG (download CSV and ingest if needed) - non-blocking
echo "📚 Setting up RAG system..."
python setup_rag.py || echo "⚠️ RAG setup incomplete - app will continue without RAG"

# Start MCP Database Server in background
echo "🔧 Starting MCP Database Server..."
python -m app.mcp.db_server &
MCP_PID=$!
echo "✅ MCP Server started with PID: $MCP_PID"

# Wait a moment for MCP server to initialize
sleep 2

# Check if MCP server is running
if ps -p $MCP_PID > /dev/null 2>&1; then
    echo "✅ MCP Server is running"
else
    echo "❌ MCP Server failed to start"
fi

# Start FastAPI application
echo "🌐 Starting FastAPI application on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
