# GCP Free Tier Deployment Guide

Complete guide for deploying AutoDealGenie on Google Cloud Platform Free Tier.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Environment Configuration](#environment-configuration)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Cost Optimization](#cost-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide helps you deploy AutoDealGenie using GCP's free tier resources to minimize costs during development and small-scale usage.

### GCP Free Tier Resources Used

- **Cloud Run**: 2 million requests/month, 360,000 GB-seconds compute time
- **Cloud Build**: 120 build-minutes/day
- **Container Registry**: 0.5GB storage
- **Secret Manager**: 6 active secrets, 10,000 access operations/month
- **Cloud Logging**: 50GB logs/month (first 50GB free)
- **Cloud Monitoring**: Free for GCP services

### Cost-Saving Features

- **In-memory caching** instead of Memorystore/Redis
- **In-memory queues** instead of Cloud Pub/Sub or hosted RabbitMQ
- **Supabase PostgreSQL** (500MB free) instead of Cloud SQL
- **Auto-scaling to zero** when not in use
- **Minimal instance sizes** (512MB-1GB memory)

---

## Prerequisites

### 1. GCP Account Setup

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Set your project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID
```

### 2. Enable Required APIs

```bash
# Enable Cloud Run, Cloud Build, and Container Registry
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 3. Configure Authentication

```bash
# Authenticate Docker with GCR
gcloud auth configure-docker
```

---

## Architecture

### Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GCP Free Tier                        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐         ┌──────────────┐              │
│  │   Frontend   │         │   Backend    │              │
│  │  (Cloud Run) │────────▶│  (Cloud Run) │              │
│  │  Next.js     │         │  FastAPI     │              │
│  │  512MB RAM   │         │  1GB RAM     │              │
│  └──────────────┘         └──────────────┘              │
│         │                        │                       │
│         │                        │                       │
│         │                        ▼                       │
│         │                 ┌──────────────┐              │
│         │                 │  Supabase    │              │
│         │                 │  PostgreSQL  │              │
│         │                 │  (External)  │              │
│         │                 └──────────────┘              │
│         │                                                │
│         │                 In-Memory:                    │
│         │                 • Cache (cachetools)          │
│         └────────────────▶• Queue (asyncio)             │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │          GCP Secret Manager                   │      │
│  │  • SECRET_KEY                                 │      │
│  │  • POSTGRES_PASSWORD                          │      │
│  │  • OPENAI_API_KEY                             │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │          Cloud Logging & Monitoring           │      │
│  │  • Application logs                           │      │
│  │  • Request metrics                            │      │
│  │  • Error tracking                             │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Request** → Frontend (Cloud Run) → Backend (Cloud Run)
2. **Backend Processing** → Supabase PostgreSQL (JSONB for unstructured data)
3. **Caching** → In-memory cache (cachetools)
4. **Async Tasks** → In-memory queue (asyncio)
5. **AI Processing** → OpenAI API

---

## Database Setup

### Option 1: Supabase PostgreSQL (Recommended)

**Free Tier**: 500MB database, 2GB bandwidth/month

1. **Create Supabase Project**
   - Go to https://supabase.com
   - Sign up and create a new project
   - Note your database password

2. **Get Connection Details**
   - Go to Project Settings → Database
   - Copy the connection string (replace `[YOUR-PASSWORD]`)
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   ```

3. **Configure Connection Pooling**
   - Enable PgBouncer in Supabase settings
   - Use port 6543 for connection pooling
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:6543/postgres
   ```

### Option 2: Self-hosted PostgreSQL on Cloud Run

**For development only** - not recommended for production

1. **Create PostgreSQL Container**
   ```bash
   # Deploy PostgreSQL to Cloud Run (not free tier optimized)
   gcloud run deploy autodealgenie-postgres \
     --image postgres:16-alpine \
     --platform managed \
     --region us-central1 \
     --memory 512Mi \
     --set-env-vars POSTGRES_PASSWORD=your-password
   ```

2. **Note**: This option is not recommended as Cloud Run is for stateless workloads

---

## Backend Deployment

### 1. Create Secret Manager Secrets

```bash
# Set environment
ENVIRONMENT="dev"  # or "prod"

# Create SECRET_KEY
echo -n "$(openssl rand -hex 32)" | \
  gcloud secrets create autodealgenie-secret-key-${ENVIRONMENT} \
    --data-file=- \
    --replication-policy="automatic"

# Create POSTGRES_PASSWORD
echo -n "your-supabase-password" | \
  gcloud secrets create autodealgenie-postgres-password-${ENVIRONMENT} \
    --data-file=- \
    --replication-policy="automatic"

# Create OPENAI_API_KEY
echo -n "your-openai-api-key" | \
  gcloud secrets create autodealgenie-openai-key-${ENVIRONMENT} \
    --data-file=- \
    --replication-policy="automatic"
```

### 2. Grant Cloud Run Access to Secrets

```bash
# Get Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant secret access
for SECRET in autodealgenie-secret-key-${ENVIRONMENT} \
              autodealgenie-postgres-password-${ENVIRONMENT} \
              autodealgenie-openai-key-${ENVIRONMENT}
do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
done
```

### 3. Build and Deploy Backend

```bash
# Navigate to repository root
cd /path/to/autodealgenie

# Deploy using Cloud Build
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=${ENVIRONMENT},_REGION=us-central1

# The deployment will create a service named:
# autodealgenie-backend-dev (or autodealgenie-backend-prod)
```

### 4. Get Backend URL

```bash
# Get the backend URL
BACKEND_URL=$(gcloud run services describe autodealgenie-backend-${ENVIRONMENT} \
  --region us-central1 \
  --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"
```

### 5. Run Database Migrations

```bash
# Option 1: Run migrations locally
export POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your-supabase-password
export POSTGRES_DB=postgres

cd backend
alembic upgrade head

# Option 2: Run migrations in Cloud Run (one-off job)
gcloud run jobs create autodealgenie-migration-${ENVIRONMENT} \
  --image gcr.io/$PROJECT_ID/autodealgenie-backend:latest \
  --region us-central1 \
  --set-env-vars ENVIRONMENT=${ENVIRONMENT} \
  --set-secrets SECRET_KEY=autodealgenie-secret-key-${ENVIRONMENT}:latest,POSTGRES_PASSWORD=autodealgenie-postgres-password-${ENVIRONMENT}:latest \
  --command alembic \
  --args upgrade,head

gcloud run jobs execute autodealgenie-migration-${ENVIRONMENT} \
  --region us-central1
```

---

## Frontend Deployment

### 1. Update Frontend Configuration

```bash
# Update the API URL in cloudbuild.yaml
# Edit frontend/cloudbuild.yaml and replace _API_URL with your backend URL
sed -i "s|_API_URL: 'https://autodealgenie-backend-dev-xxxx.a.run.app'|_API_URL: '${BACKEND_URL}'|g" \
  frontend/cloudbuild.yaml
```

### 2. Build and Deploy Frontend

```bash
# Deploy using Cloud Build
gcloud builds submit \
  --config=frontend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=${ENVIRONMENT},_REGION=us-central1,_API_URL=${BACKEND_URL}
```

### 3. Get Frontend URL

```bash
# Get the frontend URL
FRONTEND_URL=$(gcloud run services describe autodealgenie-frontend-${ENVIRONMENT} \
  --region us-central1 \
  --format="value(status.url)")

echo "Frontend URL: $FRONTEND_URL"
```

### 4. Update Backend CORS

```bash
# Update backend to allow frontend origin
gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
  --region us-central1 \
  --update-env-vars BACKEND_CORS_ORIGINS="[\"${FRONTEND_URL}\"]"
```

---

## Environment Configuration

### Development Environment

```bash
# Backend environment variables (set in Cloud Run or Secret Manager)
ENVIRONMENT=development
USE_REDIS=false
USE_RABBITMQ=false
LOG_LEVEL=DEBUG
POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
POSTGRES_USER=postgres
POSTGRES_DB=postgres
```

### Production Environment

```bash
# Backend environment variables
ENVIRONMENT=production
USE_REDIS=false
USE_RABBITMQ=false
LOG_LEVEL=INFO
POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
POSTGRES_USER=postgres
POSTGRES_DB=postgres
USE_MOCK_SERVICES=false
```

### Environment Variable Priority

1. **GCP Secret Manager** (highest priority) - for sensitive data
2. **Cloud Run environment variables** - for configuration
3. **`.env` file** - for local development only

---

## Monitoring and Logging

### Cloud Logging

```bash
# View backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=autodealgenie-backend-${ENVIRONMENT}" \
  --limit 50 \
  --format json

# View frontend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=autodealgenie-frontend-${ENVIRONMENT}" \
  --limit 50 \
  --format json

# View error logs only
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 50
```

### Cloud Monitoring

Access metrics at: https://console.cloud.google.com/monitoring

**Key Metrics to Monitor**:
- Request count and latency
- Error rate (4xx, 5xx)
- CPU and memory utilization
- Billable instance time
- Container startup time

### Set Up Alerts

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate - ${ENVIRONMENT}" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=60s
```

---

## Cost Optimization

### Free Tier Limits

**Cloud Run**:
- 2 million requests/month
- 360,000 GB-seconds compute time/month
- 180,000 vCPU-seconds compute time/month

### Optimization Strategies

1. **Scale to Zero**
   ```bash
   # Set min instances to 0 (default)
   gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
     --region us-central1 \
     --min-instances 0
   ```

2. **Reduce Memory Allocation**
   ```bash
   # Backend: 1GB (adjust based on needs)
   gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
     --region us-central1 \
     --memory 1Gi

   # Frontend: 512MB
   gcloud run services update autodealgenie-frontend-${ENVIRONMENT} \
     --region us-central1 \
     --memory 512Mi
   ```

3. **Set Request Timeout**
   ```bash
   # Reduce timeout to avoid long-running requests
   gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
     --region us-central1 \
     --timeout 60s
   ```

4. **Enable CPU Throttling**
   ```bash
   # CPU only allocated during request processing
   gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
     --region us-central1 \
     --cpu-throttling
   ```

5. **Monitor Usage**
   ```bash
   # Check billable time
   gcloud logging read "resource.type=cloud_run_revision AND metric.type=run.googleapis.com/request_count" \
     --format json | jq '.[] | .resource.labels.service_name, .metric.billable_instance_time'
   ```

### Cost Estimation

With Free Tier:
- **Cloud Run**: $0 (within free tier)
- **Supabase**: $0 (500MB free)
- **Secret Manager**: $0 (6 secrets free)
- **Cloud Build**: $0 (120 build-minutes/day free)
- **Storage**: ~$0.05/month (0.5GB images)

**Total: ~$0-1/month** (minimal overages)

---

## Troubleshooting

### Common Issues

#### 1. Deployment Fails

```bash
# Check build logs
gcloud builds list --limit 5

# Get detailed logs for a specific build
BUILD_ID="your-build-id"
gcloud builds log $BUILD_ID
```

#### 2. Service Not Responding

```bash
# Check service status
gcloud run services describe autodealgenie-backend-${ENVIRONMENT} \
  --region us-central1

# Check recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=autodealgenie-backend-${ENVIRONMENT}" \
  --limit 100 \
  --format json | jq '.[] | .textPayload, .jsonPayload'
```

#### 3. Database Connection Errors

```bash
# Test database connection from Cloud Shell
psql "postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres"

# Verify SECRET_KEY and POSTGRES_PASSWORD in Secret Manager
gcloud secrets versions access latest --secret=autodealgenie-postgres-password-${ENVIRONMENT}
```

#### 4. CORS Errors

```bash
# Update CORS origins
gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
  --region us-central1 \
  --update-env-vars BACKEND_CORS_ORIGINS="[\"${FRONTEND_URL}\",\"http://localhost:3000\"]"
```

#### 5. Cold Start Issues

```bash
# Set minimum instances (uses more free tier quota)
gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
  --region us-central1 \
  --min-instances 1
```

### Health Checks

```bash
# Backend health check
curl ${BACKEND_URL}/health

# Detailed health check
curl ${BACKEND_URL}/health/detailed

# Frontend health check
curl ${FRONTEND_URL}
```

### Rollback Deployment

```bash
# List revisions
gcloud run revisions list \
  --service autodealgenie-backend-${ENVIRONMENT} \
  --region us-central1

# Rollback to previous revision
PREVIOUS_REVISION="autodealgenie-backend-dev-00001-abc"
gcloud run services update-traffic autodealgenie-backend-${ENVIRONMENT} \
  --region us-central1 \
  --to-revisions ${PREVIOUS_REVISION}=100
```

---

## Quick Deployment Script

```bash
#!/bin/bash
# deploy-gcp.sh - Quick deployment script

set -e

ENVIRONMENT=${1:-dev}
PROJECT_ID=${2:-your-project-id}
REGION="us-central1"

echo "Deploying AutoDealGenie to GCP (${ENVIRONMENT})..."

# Set project
gcloud config set project $PROJECT_ID

# Deploy backend
echo "Deploying backend..."
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=${ENVIRONMENT},_REGION=${REGION}

# Get backend URL
BACKEND_URL=$(gcloud run services describe autodealgenie-backend-${ENVIRONMENT} \
  --region ${REGION} \
  --format="value(status.url)")

echo "Backend URL: $BACKEND_URL"

# Deploy frontend
echo "Deploying frontend..."
gcloud builds submit \
  --config=frontend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=${ENVIRONMENT},_REGION=${REGION},_API_URL=${BACKEND_URL}

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe autodealgenie-frontend-${ENVIRONMENT} \
  --region ${REGION} \
  --format="value(status.url)")

echo "Frontend URL: $FRONTEND_URL"

# Update CORS
echo "Updating CORS..."
gcloud run services update autodealgenie-backend-${ENVIRONMENT} \
  --region ${REGION} \
  --update-env-vars BACKEND_CORS_ORIGINS="[\"${FRONTEND_URL}\"]"

echo "Deployment complete!"
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
```

### Usage

```bash
chmod +x deploy-gcp.sh
./deploy-gcp.sh dev your-project-id
./deploy-gcp.sh prod your-project-id
```

---

## Next Steps

1. **Set up CI/CD**: Configure Cloud Build triggers for automatic deployments
2. **Custom Domain**: Add custom domain to Cloud Run services
3. **SSL Certificates**: Cloud Run provides automatic SSL
4. **Database Backups**: Configure Supabase automated backups
5. **Monitoring Dashboards**: Create custom Cloud Monitoring dashboards
6. **Alert Policies**: Set up email/SMS alerts for critical errors

---

## Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [GCP Free Tier](https://cloud.google.com/free)

---

## Support

For issues and questions:
- Check [Troubleshooting](#troubleshooting) section
- Review Cloud Run logs
- Open a GitHub issue
- Consult GCP documentation
