# GCP Free Tier - Quick Start Guide

Quick reference for deploying AutoDealGenie to GCP Free Tier.

## Prerequisites

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize and login
gcloud init
gcloud auth login

# Set project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID
```

## First Time Setup (5 minutes)

### 1. Enable APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 2. Set Up Supabase PostgreSQL

1. Sign up at https://supabase.com (free tier: 500MB database)
2. Create a new project
3. Get connection string from Settings → Database
4. Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres`

### 3. Create Secrets

```bash
ENVIRONMENT="dev"  # or "prod"

# SECRET_KEY (generate random)
echo -n "$(openssl rand -hex 32)" | \
  gcloud secrets create autodealgenie-secret-key-${ENVIRONMENT} \
    --data-file=- --replication-policy="automatic"

# POSTGRES_PASSWORD (from Supabase)
echo -n "your-supabase-password" | \
  gcloud secrets create autodealgenie-postgres-password-${ENVIRONMENT} \
    --data-file=- --replication-policy="automatic"

# OPENAI_API_KEY
echo -n "your-openai-api-key" | \
  gcloud secrets create autodealgenie-openai-key-${ENVIRONMENT} \
    --data-file=- --replication-policy="automatic"
```

### 4. Grant Cloud Run Access to Secrets

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for SECRET in autodealgenie-secret-key-${ENVIRONMENT} \
              autodealgenie-postgres-password-${ENVIRONMENT} \
              autodealgenie-openai-key-${ENVIRONMENT}
do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
done
```

## Deploy (2 minutes)

### Option 1: Quick Deploy Script

```bash
chmod +x deploy-gcp.sh
./deploy-gcp.sh dev your-project-id
```

### Option 2: Manual Deploy

```bash
# Deploy backend
gcloud builds submit \
  --config=backend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=dev,_REGION=us-central1

# Get backend URL
BACKEND_URL=$(gcloud run services describe autodealgenie-backend-dev \
  --region us-central1 --format="value(status.url)")

# Deploy frontend
gcloud builds submit \
  --config=frontend/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=dev,_REGION=us-central1,_API_URL=${BACKEND_URL}

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe autodealgenie-frontend-dev \
  --region us-central1 --format="value(status.url)")

# Update CORS
gcloud run services update autodealgenie-backend-dev \
  --region us-central1 \
  --update-env-vars BACKEND_CORS_ORIGINS="[\"${FRONTEND_URL}\"]"
```

## Run Database Migrations

```bash
# Option 1: Locally (requires database access)
cd backend
export POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your-supabase-password
export POSTGRES_DB=postgres
export SECRET_KEY=$(openssl rand -hex 32)
alembic upgrade head

# Option 2: Cloud Run Job (recommended)
gcloud run jobs create autodealgenie-migration-dev \
  --image gcr.io/$PROJECT_ID/autodealgenie-backend:latest \
  --region us-central1 \
  --set-secrets SECRET_KEY=autodealgenie-secret-key-dev:latest,POSTGRES_PASSWORD=autodealgenie-postgres-password-dev:latest \
  --command alembic --args upgrade,head

gcloud run jobs execute autodealgenie-migration-dev --region us-central1
```

## Verify Deployment

```bash
# Backend health check
curl https://autodealgenie-backend-dev-xxxx.a.run.app/health

# API docs
open https://autodealgenie-backend-dev-xxxx.a.run.app/docs

# Frontend
open https://autodealgenie-frontend-dev-xxxx.a.run.app
```

## Monitor

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# View metrics
open https://console.cloud.google.com/monitoring

# List services
gcloud run services list --region us-central1
```

## Update Environment Variables

```bash
# Update backend environment variable
gcloud run services update autodealgenie-backend-dev \
  --region us-central1 \
  --update-env-vars USE_REDIS=false,USE_RABBITMQ=false

# Update secret
echo -n "new-secret-value" | gcloud secrets versions add autodealgenie-secret-key-dev --data-file=-
```

## Cost Monitoring

```bash
# Check usage (should be $0-1/month on free tier)
gcloud billing accounts list
gcloud billing projects describe $PROJECT_ID

# Set up budget alert
gcloud billing budgets create \
  --billing-account YOUR_BILLING_ACCOUNT_ID \
  --display-name "AutoDealGenie Free Tier Alert" \
  --budget-amount 5USD \
  --threshold-rule threshold-percent=0.8
```

## Troubleshooting

### Build Fails

```bash
# Check build logs
gcloud builds list --limit 5
BUILD_ID="latest-build-id"
gcloud builds log $BUILD_ID
```

### Service Not Responding

```bash
# Check service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=autodealgenie-backend-dev" \
  --limit 100 --format json

# Check service status
gcloud run services describe autodealgenie-backend-dev --region us-central1
```

### Database Connection Issues

```bash
# Test database connection
psql "postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres"

# Verify secrets
gcloud secrets versions access latest --secret=autodealgenie-postgres-password-dev
```

### CORS Errors

```bash
# Update CORS to include your frontend URL
gcloud run services update autodealgenie-backend-dev \
  --region us-central1 \
  --update-env-vars BACKEND_CORS_ORIGINS="[\"https://autodealgenie-frontend-dev-xxxx.a.run.app\"]"
```

## Cleanup

```bash
# Delete all services
gcloud run services delete autodealgenie-backend-dev --region us-central1 --quiet
gcloud run services delete autodealgenie-frontend-dev --region us-central1 --quiet

# Delete secrets
gcloud secrets delete autodealgenie-secret-key-dev --quiet
gcloud secrets delete autodealgenie-postgres-password-dev --quiet
gcloud secrets delete autodealgenie-openai-key-dev --quiet

# Delete container images
gcloud container images list --repository gcr.io/$PROJECT_ID
gcloud container images delete gcr.io/$PROJECT_ID/autodealgenie-backend:latest --quiet
gcloud container images delete gcr.io/$PROJECT_ID/autodealgenie-frontend:latest --quiet
```

## Useful Commands

```bash
# Scale to zero (save costs)
gcloud run services update autodealgenie-backend-dev \
  --region us-central1 --min-instances 0

# Keep warm (faster response, uses more quota)
gcloud run services update autodealgenie-backend-dev \
  --region us-central1 --min-instances 1

# View service URL
gcloud run services describe autodealgenie-backend-dev \
  --region us-central1 --format="value(status.url)"

# Stream logs
gcloud logging tail "resource.type=cloud_run_revision"

# Test backend locally with GCP secrets
gcloud secrets versions access latest --secret=autodealgenie-secret-key-dev > /tmp/.secret
export SECRET_KEY=$(cat /tmp/.secret)
rm /tmp/.secret
```

## Environment Variables Reference

### Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | Yes | - | `development` or `production` |
| `SECRET_KEY` | Yes | - | Min 32 chars (from Secret Manager) |
| `POSTGRES_SERVER` | Yes | - | Supabase host |
| `POSTGRES_PASSWORD` | Yes | - | From Secret Manager |
| `USE_REDIS` | No | `true` | Set to `false` for free tier |
| `USE_RABBITMQ` | No | `true` | Set to `false` for free tier |
| `OPENAI_API_KEY` | Yes | - | From Secret Manager |
| `PORT` | No | `8080` | Auto-set by Cloud Run |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend Cloud Run URL |
| `NODE_ENV` | No | `production` | Set by build |
| `PORT` | No | `8080` | Auto-set by Cloud Run |

## Additional Resources

- [Full Deployment Guide](GCP_DEPLOYMENT.md)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [GCP Free Tier](https://cloud.google.com/free)

## Support

- GitHub Issues: https://github.com/Raviteja77/autodealgenie/issues
- GCP Support: https://cloud.google.com/support
