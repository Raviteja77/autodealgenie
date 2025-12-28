#!/bin/bash
# deploy-gcp.sh - Quick deployment script for GCP Cloud Run
# Usage: ./deploy-gcp.sh [dev|prod] [project-id]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
PROJECT_ID=${2:-}
REGION="us-central1"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|prod)$ ]]; then
    echo -e "${RED}Error: Environment must be 'dev' or 'prod'${NC}"
    echo "Usage: ./deploy-gcp.sh [dev|prod] [project-id]"
    exit 1
fi

# Check if project ID is provided
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: No project ID provided and no default project set${NC}"
        echo "Usage: ./deploy-gcp.sh [dev|prod] [project-id]"
        exit 1
    fi
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AutoDealGenie GCP Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Environment: ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Project ID:  ${YELLOW}${PROJECT_ID}${NC}"
echo -e "Region:      ${YELLOW}${REGION}${NC}"
echo ""

# Set project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Check if secrets exist
echo -e "${YELLOW}Checking for required secrets...${NC}"
REQUIRED_SECRETS=(
    "autodealgenie-secret-key-${ENVIRONMENT}"
    "autodealgenie-postgres-password-${ENVIRONMENT}"
    "autodealgenie-openai-key-${ENVIRONMENT}"
)

for SECRET in "${REQUIRED_SECRETS[@]}"; do
    if ! gcloud secrets describe $SECRET &>/dev/null; then
        echo -e "${RED}Error: Secret '$SECRET' not found${NC}"
        echo "Please create the secret first:"
        echo "  gcloud secrets create $SECRET --data-file=-"
        exit 1
    fi
done

echo -e "${GREEN}✓ All required secrets found${NC}"
echo ""

# Deploy backend
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying Backend...${NC}"
echo -e "${GREEN}========================================${NC}"

gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=${ENVIRONMENT},_REGION=${REGION}

if [ $? -ne 0 ]; then
    echo -e "${RED}Backend deployment failed${NC}"
    exit 1
fi

# Get backend URL
BACKEND_URL=$(gcloud run services describe autodealgenie-backend-${ENVIRONMENT} \
  --region ${REGION} \
  --format="value(status.url)")

echo ""
echo -e "${GREEN}✓ Backend deployed successfully${NC}"
echo -e "Backend URL: ${YELLOW}${BACKEND_URL}${NC}"
echo ""

# Test backend health
echo -e "${YELLOW}Testing backend health...${NC}"
if curl -f "${BACKEND_URL}/health" &>/dev/null; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Backend health check failed (might be cold start)${NC}"
fi
echo ""

# Deploy frontend
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deploying Frontend...${NC}"
echo -e "${GREEN}========================================${NC}"

gcloud builds submit \
  --config=frontend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=${ENVIRONMENT},_REGION=${REGION},_API_URL=${BACKEND_URL}

if [ $? -ne 0 ]; then
    echo -e "${RED}Frontend deployment failed${NC}"
    exit 1
fi

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe autodealgenie-frontend-${ENVIRONMENT} \
  --region ${REGION} \
  --format="value(status.url)")

echo ""
echo -e "${GREEN}✓ Frontend deployed successfully${NC}"
echo -e "Frontend URL: ${YELLOW}${FRONTEND_URL}${NC}"
echo ""

# Update CORS
echo -e "${YELLOW}Updating backend CORS settings...${NC}"
# Configure CORS origins per environment.
# - In prod, only allow the deployed frontend URL.
# - In dev, also allow common localhost origins for local development.
if [ "${ENVIRONMENT}" = "dev" ]; then
    CORS_ORIGINS="[\"${FRONTEND_URL}\",\"http://localhost:3000\",\"http://127.0.0.1:3000\"]"
else
    CORS_ORIGINS="[\"${FRONTEND_URL}\"]"
fi
gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
  --region ${REGION} \
  --update-env-vars BACKEND_CORS_ORIGINS="${CORS_ORIGINS}" \
  --quiet

echo -e "${GREEN}✓ CORS updated${NC}"
echo ""

# Test frontend health
echo -e "${YELLOW}Testing frontend health...${NC}"
if curl -f "${FRONTEND_URL}" &>/dev/null; then
    echo -e "${GREEN}✓ Frontend health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Frontend health check failed (might be cold start)${NC}"
fi
echo ""

# Display deployment summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Environment:  ${YELLOW}${ENVIRONMENT}${NC}"
echo -e "Project:      ${YELLOW}${PROJECT_ID}${NC}"
echo -e "Region:       ${YELLOW}${REGION}${NC}"
echo ""
echo -e "${GREEN}Service URLs:${NC}"
echo -e "Backend:  ${YELLOW}${BACKEND_URL}${NC}"
echo -e "Frontend: ${YELLOW}${FRONTEND_URL}${NC}"
echo ""
echo -e "${GREEN}API Documentation:${NC}"
echo -e "Swagger:  ${YELLOW}${BACKEND_URL}/docs${NC}"
echo -e "ReDoc:    ${YELLOW}${BACKEND_URL}/redoc${NC}"
echo ""
echo -e "${GREEN}Monitoring:${NC}"
echo -e "Logs:     ${YELLOW}https://console.cloud.google.com/logs${NC}"
echo -e "Metrics:  ${YELLOW}https://console.cloud.google.com/monitoring${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
