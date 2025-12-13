#!/bin/bash
# Quick start script for AutoDealGenie

set -e

echo "🚀 AutoDealGenie Quick Start"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check for .env files
if [ ! -f backend/.env ]; then
    echo "⚙️  Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your OpenAI API key"
fi

if [ ! -f frontend/.env.local ]; then
    echo "⚙️  Creating frontend/.env.local from .env.example..."
    cp frontend/.env.example frontend/.env.local
fi

echo ""
echo "🐳 Starting Docker containers..."
echo "This may take a few minutes on first run..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "🗄️  Running database migrations..."
docker compose exec backend alembic upgrade head || echo "⚠️  Migration failed - database might already be initialized"

echo ""
echo "✅ AutoDealGenie is ready!"
echo ""
echo "📱 Access the applications:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🛠️  Useful commands:"
echo "   docker compose logs -f          # View logs"
echo "   docker compose ps               # Check services status"
echo "   docker compose down             # Stop all services"
echo "   docker compose down -v          # Stop and remove volumes"
echo ""
