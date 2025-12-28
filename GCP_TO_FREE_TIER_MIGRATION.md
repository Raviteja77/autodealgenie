# Migration Guide: GCP to Free Tier Services

This guide helps you migrate from Google Cloud Platform (GCP) deployment to free tier services (Vercel + Render + Supabase + Upstash).

## Overview

**From:**
- GCP Cloud Run (Frontend & Backend)
- GCP Secret Manager
- Supabase PostgreSQL
- In-memory cache/queue

**To:**
- Vercel (Frontend)
- Render (Backend)
- Supabase PostgreSQL (same)
- Upstash Redis (cache)
- MongoDB Atlas (documents)

## Prerequisites

Before starting the migration:

1. ✅ Backup your production database
2. ✅ Create accounts on Vercel, Render, Upstash, MongoDB Atlas
3. ✅ Note all current environment variables
4. ✅ Test the new deployment in development first

## Migration Steps

### 1. Backup Current Deployment

#### Database Backup

```bash
# Backup Supabase PostgreSQL
# In Supabase Dashboard → Database → Backups
# Or using pg_dump:
pg_dump -h db.xxxxx.supabase.co -U postgres -d postgres > backup_$(date +%Y%m%d).sql

# Backup MongoDB (if using)
mongodump --uri="mongodb+srv://..." --out=./backup_$(date +%Y%m%d)
```

#### Environment Variables

```bash
# Export current GCP environment variables
# From GCP Secret Manager or Cloud Run

# Create a backup file
cat > gcp-env-backup.txt << EOF
SECRET_KEY=...
POSTGRES_SERVER=...
POSTGRES_PASSWORD=...
OPENAI_API_KEY=...
# ... all other variables
EOF
```

### 2. Set Up New Services

#### A. Upstash Redis (New)

1. Go to https://console.upstash.com/redis
2. Create database:
   - Name: `autodealgenie-prod`
   - Region: Choose closest to your Render region
   - Enable TLS
3. Note connection details:
   ```
   REDIS_HOST=xxxxx.upstash.io
   REDIS_PORT=33079
   REDIS_PASSWORD=xxxxx
   REDIS_TLS=true
   ```

#### B. MongoDB Atlas (New - Optional)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create M0 Free cluster
3. Create database user
4. Configure network access:
   - Add only trusted IP ranges (for example: Render backend egress IPs, your VPN gateway, or a bastion host).
   - For local development, you may temporarily add your current IP address, but remove it when not in use.
   - Do **not** use `0.0.0.0/0` for production environments, as it exposes your database to the entire internet.
5. Get connection string:
   ```
   MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/autodealgenie
   ```

#### C. Render Backend

1. Go to https://render.com/dashboard
2. New → Blueprint
3. Connect GitHub repository
4. Select `render.yaml`
5. Choose production service
6. Add environment variables:

```bash
# Copy from gcp-env-backup.txt
SECRET_KEY=<same-as-gcp>
POSTGRES_SERVER=<same-as-gcp>
POSTGRES_USER=<same-as-gcp>
POSTGRES_PASSWORD=<same-as-gcp>
POSTGRES_DB=<same-as-gcp>

# Add new Redis variables
REDIS_HOST=<upstash-host>
REDIS_PORT=<upstash-port>
REDIS_PASSWORD=<upstash-password>
REDIS_TLS=true

# Add MongoDB (if using)
MONGODB_URL=<mongodb-atlas-url>

# Add OpenAI
OPENAI_API_KEY=<same-as-gcp>

# CORS - will update after Vercel deployment
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

6. Deploy and wait for "Live" status
7. Note backend URL: `https://autodealgenie-backend-prod.onrender.com`

#### D. Vercel Frontend

1. Go to https://vercel.com/dashboard
2. Import GitHub repository
3. Configure:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Production Branch: `main`
4. Add environment variables:
   ```bash
   NEXT_PUBLIC_API_URL=https://autodealgenie-backend-prod.onrender.com
   NEXT_PUBLIC_API_VERSION=v1
   ```
5. Deploy and wait for "Ready" status
6. Note frontend URL: `https://autodealgenie.vercel.app`

#### E. Update Backend CORS

1. Go to Render → Backend Service → Environment
2. Update `BACKEND_CORS_ORIGINS`:
   ```json
   ["https://autodealgenie.vercel.app"]
   ```
3. Save and redeploy

### 3. Migrate Data (If Needed)

If you're changing Supabase instances or databases:

```bash
# 1. Dump from old database
pg_dump -h old-db.supabase.co -U postgres -d postgres > migration.sql

# 2. Restore to new database
psql -h new-db.supabase.co -U postgres -d postgres < migration.sql

# 3. Verify data
psql -h new-db.supabase.co -U postgres -d postgres
\dt  # List tables
SELECT COUNT(*) FROM users;  # Verify data
```

### 4. Test New Deployment

#### A. Health Checks

```bash
# Test backend
curl https://autodealgenie-backend-prod.onrender.com/health

# Expected response:
# {"status":"healthy","timestamp":"..."}

# Test frontend
curl https://autodealgenie.vercel.app

# Should return HTML
```

#### B. Database Connection

```bash
# From Render Shell:
cd backend
python -c "
from app.db.session import SessionLocal
db = SessionLocal()
try:
    db.execute('SELECT 1')
    print('Database connected!')
finally:
    db.close()
"
```

#### C. Redis Connection

```bash
# Test Redis connection
redis-cli -h <upstash-host> -p <upstash-port> -a <password> --tls ping
# Expected: PONG
```

#### D. End-to-End Testing

1. Open frontend in browser: `https://autodealgenie.vercel.app`
2. Test user registration
3. Test login/logout
4. Create a test deal
5. Verify data in database

### 5. Update DNS (If Using Custom Domain)

#### For Vercel:

```bash
# Add DNS records:
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

#### For Render:

```bash
# Add DNS records:
Type: CNAME
Name: api
Value: autodealgenie-backend-prod.onrender.com
```

### 6. Monitoring and Alerts

#### Vercel

1. Go to Project → Analytics
2. Monitor traffic and errors
3. Set up email notifications

#### Render

1. Go to Dashboard → Notifications
2. Add email for deploy failures
3. Monitor logs regularly

#### Upstash

1. Go to Database → Metrics
2. Monitor command usage
3. Set alert at 80% of daily limit

### 7. Decommission GCP Resources

⚠️ **ONLY after verifying new deployment is working!**

```bash
# 1. Stop Cloud Run services
gcloud run services delete autodealgenie-frontend-prod --region us-central1
gcloud run services delete autodealgenie-backend-prod --region us-central1

# 2. Delete Secret Manager secrets (optional)
gcloud secrets delete autodealgenie-secret-key-prod
gcloud secrets delete autodealgenie-postgres-password-prod
gcloud secrets delete autodealgenie-openai-key-prod

# 3. Delete container images (optional)
gcloud container images delete gcr.io/$PROJECT_ID/autodealgenie-frontend:latest
gcloud container images delete gcr.io/$PROJECT_ID/autodealgenie-backend:latest

# 4. Keep Supabase database (same for both deployments)
```

## Rollback Plan

If something goes wrong with the migration:

### Quick Rollback to GCP

```bash
# 1. Redeploy GCP services
./deploy-gcp.sh prod your-project-id

# 2. Update DNS to point back to GCP (if changed)
# Revert DNS changes

# 3. Notify users of temporary downtime
```

### Partial Rollback

You can run both deployments simultaneously:
- GCP for production traffic
- Free tier for testing/development

Update DNS gradually using weighted routing.

## Cost Comparison

### Before (GCP Free Tier)

- Cloud Run: $0 (within free tier)
- Supabase: $0 (within free tier)
- Total: **$0/month**

### After (Free Tier Services)

- Vercel: $0 (within free tier)
- Render: $0 (within free tier)
- Supabase: $0 (within free tier)
- Upstash: $0 (within free tier)
- MongoDB Atlas: $0 (within free tier)
- Total: **$0/month**

### Benefits of Migration

✅ **Pros:**
- Better frontend performance (Vercel CDN)
- Redis caching (better than in-memory)
- Separate development and production services
- Automatic preview deployments (Vercel)
- Simpler deployment process

⚠️ **Cons:**
- Backend cold starts (~30-60s on Render free tier)
- Multiple services to manage
- Rate limits on free tiers

## Troubleshooting

### Issue: Backend won't start on Render

**Check:**
1. All environment variables are set
2. Build command is correct
3. No syntax errors in code
4. Database is accessible

**Solution:**
```bash
# Check logs in Render dashboard
# Common fixes:
# - Add missing environment variables
# - Verify database connection string
# - Check Python version (3.11+)
```

### Issue: Frontend can't connect to backend

**Check:**
1. NEXT_PUBLIC_API_URL is correct
2. Backend CORS includes frontend URL
3. Backend is not spun down

**Solution:**
```bash
# Wake up backend
curl https://autodealgenie-backend-prod.onrender.com/health

# Verify CORS in Render environment variables
# Redeploy if needed
```

### Issue: Database connection fails

**Check:**
1. Supabase is same instance
2. Connection string is correct
3. Network access is allowed

**Solution:**
```bash
# Test connection
psql "postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres"

# If fails, check:
# - Password is correct
# - Supabase project is active
# - Connection pooling port (6543) vs direct (5432)
```

## Post-Migration Checklist

- [ ] All services deployed and running
- [ ] Database connected and migrations applied
- [ ] Redis connected (no errors in logs)
- [ ] Frontend loads correctly
- [ ] User authentication works
- [ ] Can create/read/update/delete data
- [ ] AI features working (OpenAI API)
- [ ] Custom domain configured (if applicable)
- [ ] Monitoring and alerts set up
- [ ] GCP services decommissioned
- [ ] Documentation updated with new URLs
- [ ] Team notified of new deployment

## Support

If you encounter issues during migration:

1. Check [FREE_TIER_DEPLOYMENT.md](FREE_TIER_DEPLOYMENT.md) for detailed setup
2. Review service logs (Render, Vercel, Supabase)
3. Test individual components (database, Redis, API)
4. Create an issue on GitHub with details

---

**Estimated Migration Time:** 1-2 hours

**Recommended Migration Window:** Off-peak hours or during maintenance window

**Success Rate:** High (both deployments use same database and similar architecture)
