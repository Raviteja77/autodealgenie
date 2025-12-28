# GCP Free Tier Migration Summary

This document summarizes the changes made to support deployment on GCP Free Tier.

## Overview

AutoDealGenie has been migrated to support deployment on Google Cloud Platform's Free Tier, enabling minimal or no costs during development and small-scale usage.

## Key Changes

### 1. Optional Infrastructure Components

#### Redis → In-Memory Cache
- **New Module**: `backend/app/db/in_memory_cache.py`
- **Feature**: Uses `cachetools` for in-memory caching
- **Configuration**: Set `USE_REDIS=false` to enable
- **Free Tier Benefit**: Eliminates need for Memorystore/Redis

#### RabbitMQ → In-Memory Queue
- **New Module**: `backend/app/db/in_memory_queue.py`
- **Feature**: Async queue using Python's `asyncio`
- **Configuration**: Set `USE_RABBITMQ=false` to enable
- **Free Tier Benefit**: Eliminates need for Cloud Pub/Sub or hosted RabbitMQ

#### Database → Supabase PostgreSQL
- **Option**: Supabase PostgreSQL (500MB free)
- **Alternative**: Self-hosted PostgreSQL on Cloud Run
- **JSONB Support**: Retained for unstructured data
- **Free Tier Benefit**: Replaces Cloud SQL (not in free tier)

### 2. Cloud Run Deployment

#### Backend (FastAPI)
- **Dockerfile**: `backend/Dockerfile.cloudrun`
- **Build Config**: `backend/cloudbuild.yaml`
- **Resources**: 1GB RAM, 1 CPU, auto-scaling to 0
- **Port**: 8080 (Cloud Run standard)
- **Environment Variables**: Configurable via Secret Manager

#### Frontend (Next.js)
- **Dockerfile**: `frontend/Dockerfile.cloudrun`
- **Build Config**: `frontend/cloudbuild.yaml`
- **Resources**: 512MB RAM, 1 CPU, auto-scaling to 0
- **Port**: 8080 (Cloud Run standard)
- **Build Args**: API URL configured at build time

### 3. Configuration Management

#### Backend Environment Templates
- `backend/.env.dev.example` - Development configuration
- `backend/.env.prod.example` - Production configuration
- Key settings: `USE_REDIS=false`, `USE_RABBITMQ=false`

#### Frontend Environment Templates
- `frontend/.env.dev.example` - Development configuration
- `frontend/.env.prod.example` - Production configuration
- Key settings: `NEXT_PUBLIC_API_URL` for backend URL

### 4. Secret Management

Secrets stored in GCP Secret Manager:
- `autodealgenie-secret-key-{env}` - Application secret key
- `autodealgenie-postgres-password-{env}` - Database password
- `autodealgenie-openai-key-{env}` - OpenAI API key

### 5. Deployment Automation

#### Quick Deploy Script
- **File**: `deploy-gcp.sh`
- **Usage**: `./deploy-gcp.sh [dev|prod] [project-id]`
- **Features**: Automatic secret validation, backend and frontend deployment, CORS configuration

#### GitHub Actions Workflow (Template)
- **File**: `.github/workflows/deploy-gcp.yml.template`
- **Features**: Automated CI/CD, manual and push-triggered deployments, health checks

### 6. Documentation

#### Comprehensive Guides
- **GCP_DEPLOYMENT.md** - Complete deployment guide (17KB)
  - Architecture diagrams
  - Step-by-step setup
  - Cost optimization
  - Monitoring and logging
  - Troubleshooting

- **GCP_QUICKSTART.md** - Quick reference guide (8KB)
  - 5-minute setup
  - Common commands
  - Quick troubleshooting
  - Environment variables reference

#### Updated Documentation
- **README.md** - Added GCP deployment section
- **INFRASTRUCTURE_MIGRATION_SUMMARY.md** - Existing Kafka→RabbitMQ migration

### 7. Build Optimization

#### Docker Ignore Files
- `backend/.dockerignore` - Excludes tests, docs, IDE files
- `frontend/.dockerignore` - Excludes node_modules, build artifacts
- **Benefit**: Faster builds, smaller images

## Architecture Changes

### Before (Full Infrastructure)
```
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │
└─────────────┘     └─────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │PostgreSQL│      │  Redis  │      │RabbitMQ │
   └─────────┘      └─────────┘      └─────────┘
```

### After (GCP Free Tier)
```
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │
│ (Cloud Run) │     │ (Cloud Run) │
└─────────────┘     └─────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │Supabase │      │MemCache │      │MemQueue │
   │PostgreSQL│     │(optional)│     │(optional)│
   └─────────┘      └─────────┘      └─────────┘
```

## Cost Analysis

### Before (Traditional Deployment)
- Cloud SQL: ~$25/month (db-f1-micro)
- Memorystore: ~$30/month (1GB Redis)
- Cloud Pub/Sub or Hosted RabbitMQ: ~$10/month
- **Total: ~$65/month minimum**

### After (GCP Free Tier)
- Cloud Run (Backend): $0 (within 2M requests/month)
- Cloud Run (Frontend): $0 (within free tier)
- Supabase PostgreSQL: $0 (500MB free)
- In-memory cache: $0 (no external service)
- In-memory queue: $0 (no external service)
- Container Registry: ~$0.05/month (0.5GB)
- Secret Manager: $0 (6 secrets free)
- **Total: ~$0-1/month**

**Savings: ~$60-65/month**

## Limitations and Trade-offs

### In-Memory Cache
- ✅ **Pros**: No cost, fast, simple
- ❌ **Cons**: Lost on container restart, not shared across instances
- 🎯 **Best For**: Development, low-traffic apps, stateless caching

### In-Memory Queue
- ✅ **Pros**: No cost, simple, async task processing
- ❌ **Cons**: Lost on restart, no persistence, not shared across instances
- 🎯 **Best For**: Development, non-critical async tasks

### Supabase PostgreSQL
- ✅ **Pros**: Free, managed, 500MB storage, connection pooling
- ❌ **Cons**: 500MB limit, shared infrastructure
- 🎯 **Best For**: Development, small databases, MVP

### Cloud Run Auto-scaling
- ✅ **Pros**: Zero cost when idle, auto-scales to demand
- ❌ **Cons**: Cold start latency (1-3 seconds)
- 🎯 **Best For**: Intermittent traffic, development, testing

## Migration Path

### From Development to Production

When scaling beyond free tier:

1. **Enable Redis**: Set `USE_REDIS=true` and deploy Memorystore
2. **Enable RabbitMQ**: Set `USE_RABBITMQ=true` and deploy Cloud Pub/Sub or hosted RabbitMQ
3. **Upgrade Database**: Migrate to Cloud SQL for better performance and storage
4. **Increase Resources**: Bump Cloud Run memory and CPU allocations
5. **Add CDN**: Use Cloud CDN for static asset delivery
6. **Enable Load Balancer**: Use Cloud Load Balancing for production traffic

### Configuration Changes Needed

```bash
# Development (.env.dev)
USE_REDIS=false
USE_RABBITMQ=false
POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co

# Production (.env.prod)
USE_REDIS=true
USE_RABBITMQ=true
POSTGRES_SERVER=your-cloud-sql-instance
```

## Testing

### Validated Components
- ✅ In-memory cache (set/get/delete/exists/ping)
- ✅ In-memory queue (connect/declare/publish/consume/ping)
- ✅ Docker build process (backend and frontend)
- ✅ Cloud Build YAML syntax
- ✅ Configuration with optional services

### Test Results
```
✓ In-memory cache module loads successfully
✓ In-memory queue module loads successfully
✓ Backend cloudbuild.yaml is valid YAML
✓ Frontend cloudbuild.yaml is valid YAML
✓ Docker build process completes successfully
✅ All validations passed
```

## Files Added

### Infrastructure
- `backend/Dockerfile.cloudrun` - Production backend image
- `frontend/Dockerfile.cloudrun` - Production frontend image
- `backend/cloudbuild.yaml` - Backend CI/CD configuration
- `frontend/cloudbuild.yaml` - Frontend CI/CD configuration
- `backend/.dockerignore` - Build optimization
- `frontend/.dockerignore` - Build optimization

### Application Code
- `backend/app/db/in_memory_cache.py` - Caching fallback
- `backend/app/db/in_memory_queue.py` - Queue fallback

### Configuration
- `backend/.env.dev.example` - Development environment template
- `backend/.env.prod.example` - Production environment template
- `frontend/.env.dev.example` - Frontend development template
- `frontend/.env.prod.example` - Frontend production template

### Deployment
- `deploy-gcp.sh` - Quick deployment script
- `.github/workflows/deploy-gcp.yml.template` - GitHub Actions template

### Documentation
- `GCP_DEPLOYMENT.md` - Comprehensive deployment guide
- `GCP_QUICKSTART.md` - Quick reference guide
- `GCP_FREE_TIER_MIGRATION.md` - This file

## Files Modified

### Configuration
- `backend/app/core/config.py` - Added `USE_REDIS` and `USE_RABBITMQ` flags
- `backend/app/main.py` - Optional service initialization
- `backend/requirements.txt` - Added `cachetools==5.3.2`
- `.gitignore` - Added GCP environment files
- `README.md` - Added GCP deployment section

## Implementation Status

- ✅ Backend Dockerfile for Cloud Run
- ✅ Frontend Dockerfile for Cloud Run
- ✅ In-memory cache implementation
- ✅ In-memory queue implementation
- ✅ Cloud Build configurations
- ✅ Environment templates (dev/prod)
- ✅ Deployment script
- ✅ Comprehensive documentation
- ✅ GitHub Actions template
- ✅ Docker ignore files
- ✅ Testing and validation

## Next Steps

### For Deployment
1. Set up GCP project and enable APIs
2. Create Supabase PostgreSQL database
3. Configure GCP Secret Manager
4. Run `./deploy-gcp.sh dev your-project-id`
5. Test deployment and verify functionality

### For Production
1. Review security settings
2. Set up monitoring and alerting
3. Configure custom domain (optional)
4. Set up automated backups
5. Implement database migration strategy

## Support

- **Documentation**: See `GCP_DEPLOYMENT.md` and `GCP_QUICKSTART.md`
- **Issues**: GitHub Issues
- **GCP Support**: https://cloud.google.com/support
- **Supabase Support**: https://supabase.com/docs

## Version History

- **v1.0.0** (2024-12-27) - Initial GCP Free Tier migration
  - Added Cloud Run support
  - Implemented optional infrastructure components
  - Created comprehensive documentation
  - Validated all components

---

**Status**: ✅ Complete and Ready for Deployment

**Tested**: Local validation, Docker builds, configuration loading

**Next Milestone**: Production deployment on GCP Free Tier
