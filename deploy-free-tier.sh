#!/bin/bash

# Free Tier Deployment Setup Script
# This script helps you set up AutoDealGenie on free tier services

set -e

echo "=================================="
echo "AutoDealGenie Free Tier Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if required commands are available
command -v openssl >/dev/null 2>&1 || { print_error "openssl is required but not installed. Aborting."; exit 1; }

echo "This script will guide you through setting up AutoDealGenie on free tier services."
echo ""
echo "Prerequisites:"
echo "  1. GitHub account (for source control)"
echo "  2. Vercel account (for frontend hosting)"
echo "  3. Render account (for backend hosting)"
echo "  4. Supabase account (for PostgreSQL database)"
echo "  5. Upstash account (for Redis cache)"
echo "  6. MongoDB Atlas account (for document storage)"
echo "  7. OpenAI API key (for AI features)"
echo ""

read -p "Have you created all the required accounts? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please create the required accounts first:"
    echo "  - Vercel: https://vercel.com"
    echo "  - Render: https://render.com"
    echo "  - Supabase: https://supabase.com"
    echo "  - Upstash: https://upstash.com"
    echo "  - MongoDB Atlas: https://www.mongodb.com/cloud/atlas"
    echo "  - OpenAI: https://platform.openai.com"
    echo ""
    exit 1
fi

echo ""
echo "=================================="
echo "Step 1: Generate SECRET_KEY"
echo "=================================="
echo ""

SECRET_KEY=$(openssl rand -hex 32)
print_info "Generated SECRET_KEY: $SECRET_KEY"
echo ""

echo "Save this SECRET_KEY - you'll need it for Render configuration!"
echo ""
read -p "Press Enter to continue..."
echo ""

echo "=================================="
echo "Step 2: Environment Configuration"
echo "=================================="
echo ""

# Create temporary env file for user to fill in
cat > /tmp/autodealgenie-env.txt << EOF
# Copy these values and add them to your Render dashboard
# Render Dashboard → Service → Settings → Environment

SECRET_KEY=$SECRET_KEY

# Supabase PostgreSQL (https://supabase.com)
# Get from: Project Settings → Database → Connection String
POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your-supabase-password>
POSTGRES_DB=postgres
POSTGRES_PORT=5432

# MongoDB Atlas (https://www.mongodb.com/cloud/atlas)
# Get from: Clusters → Connect → Connect your application
MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/autodealgenie?retryWrites=true&w=majority

# Upstash Redis (https://upstash.com)
# Get from: Console → Redis → Details
REDIS_HOST=<your-redis-host>.upstash.io
REDIS_PORT=<your-redis-port>
REDIS_PASSWORD=<your-redis-password>
REDIS_DB=0
REDIS_TLS=true

# OpenAI API (https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-<your-openai-api-key>

# CORS Origins (update after deploying frontend)
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

EOF

chmod 600 /tmp/autodealgenie-env.txt
print_info "Created environment template at: /tmp/autodealgenie-env.txt"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your services:"
echo "   - Supabase: Create PostgreSQL database"
echo "   - MongoDB Atlas: Create cluster and database user"
echo "   - Upstash: Create Redis database"
echo "   - Get your OpenAI API key"
echo ""
echo "2. Fill in the values in /tmp/autodealgenie-env.txt"
echo ""
echo "3. Deploy backend to Render:"
echo "   a. Go to https://render.com/dashboard"
echo "   b. New → Web Service"
echo "   c. Connect your GitHub repository"
echo "   d. Configure:"
echo "      - Name: autodealgenie-backend-dev"
echo "      - Branch: dev"
echo "      - Build Command: cd backend && pip install -r requirements.txt"
echo "      - Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "   e. Add environment variables from /tmp/autodealgenie-env.txt"
echo ""
echo "4. Run database migrations:"
echo "   a. Open Render Shell (Dashboard → Service → Shell)"
echo "   b. Run: cd backend && alembic upgrade head"
echo ""
echo "5. Deploy frontend to Vercel:"
echo "   a. Go to https://vercel.com/dashboard"
echo "   b. New Project → Import Git Repository"
echo "   c. Configure:"
echo "      - Framework: Next.js"
echo "      - Root Directory: frontend"
echo "   d. Add environment variables:"
echo "      - NEXT_PUBLIC_API_URL: <your-render-backend-url>"
echo "      - NEXT_PUBLIC_API_VERSION: v1"
echo ""
echo "6. Update CORS in Render:"
echo "   - Add your Vercel URL to BACKEND_CORS_ORIGINS"
echo ""
echo "For detailed instructions, see FREE_TIER_DEPLOYMENT.md"
echo ""

cat /tmp/autodealgenie-env.txt
echo ""
print_warning "Environment template saved to: /tmp/autodealgenie-env.txt"
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
