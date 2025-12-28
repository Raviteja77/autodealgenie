# Free Tier Deployment Guide

Complete guide for deploying AutoDealGenie using free services from Vercel, Render, Supabase, Upstash, and MongoDB Atlas.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Database Setup](#database-setup)
5. [Backend Deployment (Render)](#backend-deployment-render)
6. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
7. [Environment Configuration](#environment-configuration)
8. [Branch Strategy](#branch-strategy)
9. [Troubleshooting](#troubleshooting)
10. [Cost Optimization](#cost-optimization)

---

## Overview

This guide helps you deploy AutoDealGenie using 100% free services, perfect for development, testing, and low-traffic production environments.

### Services Used

| Service | Purpose | Free Tier Limits |
|---------|---------|-----------------|
| **Vercel** | Frontend hosting (Next.js) | Unlimited deployments, 100GB bandwidth/month |
| **Render** | Backend hosting (FastAPI) | 750 hours/month, spins down after 15min idle |
| **Supabase** | PostgreSQL database | 500MB database, unlimited API requests |
| **Upstash** | Redis cache | 10,000 commands/day |
| **MongoDB Atlas** | Document database | 512MB storage |

### Total Monthly Cost

**$0** (within free tier limits) 🎉

---

## Prerequisites

### 1. Required Accounts

Create free accounts on:
- [Vercel](https://vercel.com) - Frontend hosting
- [Render](https://render.com) - Backend hosting
- [Supabase](https://supabase.com) - PostgreSQL database
- [Upstash](https://upstash.com) - Redis cache
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Document database
- [GitHub](https://github.com) - Source code repository

### 2. GitHub Repository

Ensure your AutoDealGenie code is in a GitHub repository with:
- `main` branch for production
- `dev` branch for development

```bash
# Create dev branch if it doesn't exist
git checkout -b dev
git push -u origin dev
```

### 3. Required Tools (for local setup)

- `openssl` - For generating secret keys
- `git` - Version control
- `curl` - Testing API endpoints

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Free Tier Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   Vercel CDN     │         │   Render         │         │
│  │   (Frontend)     │────────▶│   (Backend)      │         │
│  │   Next.js 14     │  HTTPS  │   FastAPI        │         │
│  │   Edge Functions │         │   Python 3.11    │         │
│  └──────────────────┘         └──────────────────┘         │
│         │                              │                     │
│         │                              │                     │
│         │                              ▼                     │
│         │                     ┌──────────────────┐          │
│         │                     │   Supabase       │          │
│         │                     │   PostgreSQL 16  │          │
│         │                     │   500MB Storage  │          │
│         │                     └──────────────────┘          │
│         │                              │                     │
│         │                              │                     │
│         │                     ┌──────────────────┐          │
│         │                     │  MongoDB Atlas   │          │
│         │                     │  Document Store  │          │
│         │                     │  512MB Storage   │          │
│         │                     └──────────────────┘          │
│         │                              │                     │
│         │                              │                     │
│         └─────────────────────────────▶│                     │
│                                ┌──────────────────┐          │
│                                │  Upstash Redis   │          │
│                                │  Cache Layer     │          │
│                                │  10k cmds/day    │          │
│                                └──────────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘

External Services:
• OpenAI API (AI features)
• MarketCheck API (vehicle data)
```

### Data Flow

1. **User Request** → Vercel CDN → Next.js Frontend
2. **API Call** → Render Backend (FastAPI)
3. **Data Storage** → Supabase (PostgreSQL) + MongoDB Atlas
4. **Caching** → Upstash Redis (session, API responses)
5. **AI Processing** → OpenAI API

---

## Database Setup

### 1. Supabase PostgreSQL

**Purpose**: Primary relational database for users, deals, loan applications

1. **Create Project**:
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Name: `autodealgenie-dev` (for development) or `autodealgenie-prod` (for production)
   - Generate a strong database password
   - Region: Choose closest to your users
   - Wait for project creation (~2 minutes)

2. **Get Connection Details**:
   - Go to Project Settings → Database
   - Copy the connection string:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
     ```
   - Save these values for later:
     - `POSTGRES_SERVER`: `db.xxxxxxxxxxxx.supabase.co`
     - `POSTGRES_USER`: `postgres`
     - `POSTGRES_PASSWORD`: Your password
     - `POSTGRES_DB`: `postgres`
     - `POSTGRES_PORT`: `5432`

3. **Enable Connection Pooling** (Recommended):
   - Go to Project Settings → Database → Connection Pooling
   - Enable "Session mode"
   - Use port `6543` for pooling (better for serverless)
   - Update `POSTGRES_PORT` to `6543` in your environment variables

4. **Configure Network Access**:
   - Supabase automatically allows connections from anywhere
   - No additional configuration needed

### 2. MongoDB Atlas

**Purpose**: Document database for search history, negotiation conversations, vehicle cache

1. **Create Cluster**:
   - Go to https://www.mongodb.com/cloud/atlas
   - Click "Build a Database"
   - Choose "Free" (M0 Sandbox)
   - Provider: AWS (or your preference)
   - Region: Choose closest to your users
   - Cluster Name: `autodealgenie`
   - Click "Create"

2. **Create Database User**:
   - Go to Database Access → Add New Database User
   - Authentication Method: Password
   - Username: `autodealgenie`
   - Password: Generate a strong password
   - Database User Privileges: "Atlas admin"
   - Click "Add User"

3. **Configure Network Access**:
   - Go to Network Access → Add IP Address
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Or add specific Render IP addresses
   - Click "Confirm"

4. **Get Connection String**:
   - Go to Database → Connect → Connect your application
   - Driver: Python, Version: 3.6 or later
   - Copy connection string:
     ```
     mongodb+srv://autodealgenie:<password>@autodealgenie.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - Replace `<password>` with your user password
   - Add database name: `/autodealgenie`
   - Final format:
     ```
     mongodb+srv://autodealgenie:YOUR_PASSWORD@autodealgenie.xxxxx.mongodb.net/autodealgenie?retryWrites=true&w=majority
     ```
   - Save this as `MONGODB_URL`

### 3. Upstash Redis

**Purpose**: Cache layer for session management, API responses, rate limiting

1. **Create Database**:
   - Go to https://console.upstash.com/redis
   - Click "Create Database"
   - Name: `autodealgenie-dev` (or `-prod` for production)
   - Type: Regional
   - Region: Choose closest to your Render deployment
   - TLS: Enabled (required)
   - Click "Create"

2. **Get Connection Details**:
   - Go to your database → Details
   - Copy these values:
     - `REDIS_HOST`: `xxxxxx-xxxxx-xxxx.upstash.io`
     - `REDIS_PORT`: Usually `6379` or `33079`
     - `REDIS_PASSWORD`: Copy from "Password" field
   - Additional settings:
     - `REDIS_DB`: `0`
     - `REDIS_TLS`: `true` (Upstash requires TLS)

3. **Configure Access**:
   - Upstash allows connections from anywhere by default
   - No additional configuration needed

---

## Backend Deployment (Render)

### Method 1: Using Blueprint (Recommended)

1. **Prepare Repository**:
   - Ensure `render.yaml` is in your repository root
   - Commit and push to GitHub

2. **Create Render Account**:
   - Go to https://render.com
   - Sign up with GitHub

3. **Deploy with Blueprint**:
   - Dashboard → "New" → "Blueprint"
   - Connect your GitHub repository
   - Select repository: `autodealgenie`
   - Render will detect `render.yaml`
   - Click "Apply"

4. **Configure Environment Variables**:
   - Go to each service (dev and prod)
   - Settings → Environment
   - Add secret variables (marked as `sync: false` in `render.yaml`):
     ```bash
     SECRET_KEY=<generate-with-openssl-rand-hex-32>
     POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
     POSTGRES_USER=postgres
     POSTGRES_PASSWORD=<your-supabase-password>
     POSTGRES_DB=postgres
     MONGODB_URL=mongodb+srv://...
     REDIS_HOST=<upstash-host>.upstash.io
     REDIS_PORT=<upstash-port>
     REDIS_PASSWORD=<upstash-password>
     OPENAI_API_KEY=sk-<your-openai-key>
     ```

5. **Generate SECRET_KEY**:
   ```bash
   openssl rand -hex 32
   ```

6. **Deploy**:
   - Services will automatically deploy
   - Monitor logs in Render dashboard
   - Wait for "Live" status

7. **Get Backend URLs**:
   - Development: `https://autodealgenie-backend-dev.onrender.com`
   - Production: `https://autodealgenie-backend-prod.onrender.com`
   - Save these URLs for frontend configuration

### Method 2: Manual Setup

1. **Create Web Service**:
   - Dashboard → "New" → "Web Service"
   - Connect GitHub repository
   - Name: `autodealgenie-backend-dev`
   - Region: Oregon (or closest)
   - Branch: `dev`
   - Root Directory: Leave empty
   - Runtime: Python 3
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free

2. **Add Environment Variables**:
   - Same as Method 1, step 4

3. **Repeat for Production**:
   - Create another service with branch: `main`
   - Name: `autodealgenie-backend-prod`

### Run Database Migrations

**Important**: Run migrations once after first deployment

#### Option 1: Render Shell

```bash
# Open Render Shell (Dashboard → Service → Shell)
cd backend
alembic upgrade head
```

#### Option 2: Local Terminal

```bash
# Set environment variables
export POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=<your-password>
export POSTGRES_DB=postgres
export SECRET_KEY=$(openssl rand -hex 32)

# Run migrations
cd backend
alembic upgrade head
```

---

## Frontend Deployment (Vercel)

### 1. Import Project

1. **Sign in to Vercel**:
   - Go to https://vercel.com
   - Sign in with GitHub

2. **Import Repository**:
   - Dashboard → "Add New" → "Project"
   - Import your GitHub repository
   - Select `autodealgenie`

3. **Configure Project**:
   - Framework Preset: **Next.js** (auto-detected)
   - Root Directory: **frontend**
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
   - Install Command: `npm install` (default)

### 2. Configure Environment Variables

1. **Go to Settings → Environment Variables**

2. **Add Variables**:

   **For Development (Preview - dev branch)**:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://autodealgenie-backend-dev.onrender.com
   Environments: Preview ✓
   
   Name: NEXT_PUBLIC_API_VERSION
   Value: v1
   Environments: Preview ✓
   ```

   **For Production (main branch)**:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://autodealgenie-backend-prod.onrender.com
   Environments: Production ✓
   
   Name: NEXT_PUBLIC_API_VERSION
   Value: v1
   Environments: Production ✓
   ```

### 3. Configure Git Integration

1. **Go to Settings → Git**:
   - Production Branch: `main`
   - Enable "Automatic deployments"
   - Enable "Preview deployments" for all branches

2. **Branch Protection**:
   - Consider enabling branch protection for `main` in GitHub
   - Require pull request reviews before merging

### 4. Deploy

1. **First Deployment**:
   - Vercel automatically deploys on import
   - Monitor deployment logs
   - Wait for "Ready" status

2. **Get Deployment URLs**:
   - Production: `https://<your-project>.vercel.app`
   - Development: `https://<your-project>-<hash>-<team>.vercel.app`
   - Each commit to `dev` creates a new preview deployment

### 5. Update Backend CORS

**Critical**: Update backend to accept requests from frontend

1. **Go to Render Dashboard**:
   - Select backend service (dev or prod)
   - Settings → Environment

2. **Update BACKEND_CORS_ORIGINS**:
   ```json
   ["https://your-project.vercel.app","https://your-project-dev.vercel.app"]
   ```

3. **Save and Redeploy**:
   - Click "Save Changes"
   - Service will automatically redeploy

---

## Environment Configuration

### Development Environment (.env.dev)

**Backend** (Render - dev branch):
```bash
ENVIRONMENT=development
SECRET_KEY=<generated-secret>
POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<supabase-password>
POSTGRES_DB=postgres
POSTGRES_PORT=5432
MONGODB_URL=mongodb+srv://...
REDIS_HOST=<upstash-host>.upstash.io
REDIS_PORT=<upstash-port>
REDIS_PASSWORD=<upstash-password>
REDIS_DB=0
REDIS_TLS=true
OPENAI_API_KEY=sk-<your-key>
LOG_LEVEL=DEBUG
BACKEND_CORS_ORIGINS=["https://your-app-dev.vercel.app","http://localhost:3000"]
```

**Frontend** (Vercel - dev branch):
```bash
NEXT_PUBLIC_API_URL=https://autodealgenie-backend-dev.onrender.com
NEXT_PUBLIC_API_VERSION=v1
```

### Production Environment (.env.prod)

**Backend** (Render - main branch):
```bash
ENVIRONMENT=production
SECRET_KEY=<generated-secret>
POSTGRES_SERVER=db.xxxxxxxxxxxx.supabase.co
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<supabase-password>
POSTGRES_DB=postgres
POSTGRES_PORT=5432
MONGODB_URL=mongodb+srv://...
REDIS_HOST=<upstash-host>.upstash.io
REDIS_PORT=<upstash-port>
REDIS_PASSWORD=<upstash-password>
REDIS_DB=0
REDIS_TLS=true
OPENAI_API_KEY=sk-<your-key>
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]
```

**Frontend** (Vercel - main branch):
```bash
NEXT_PUBLIC_API_URL=https://autodealgenie-backend-prod.onrender.com
NEXT_PUBLIC_API_VERSION=v1
```

---

## Branch Strategy

### Git Workflow

```
main (production)
  ↑
  │ PR + Review
  │
dev (development)
  ↑
  │ Feature PRs
  │
feature/* (feature branches)
```

### Deployment Flow

1. **Feature Development**:
   - Create feature branch: `git checkout -b feature/new-feature`
   - Develop and test locally
   - Push: `git push origin feature/new-feature`
   - Vercel creates preview deployment

2. **Merge to Dev**:
   - Create PR: `feature/new-feature` → `dev`
   - Review and merge
   - Triggers deployments:
     - Vercel: Preview deployment (dev branch)
     - Render: Dev backend service

3. **Merge to Main**:
   - Create PR: `dev` → `main`
   - Review and approve
   - Merge triggers production deployments:
     - Vercel: Production deployment
     - Render: Prod backend service

### Branch Protection

Configure in GitHub Settings → Branches:

**For `main` branch**:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Include administrators

**For `dev` branch**:
- ✅ Require pull request reviews (optional)
- ✅ Require status checks to pass

---

## Troubleshooting

### Backend Issues

#### 1. Service Not Starting

**Symptoms**: Deployment fails, service shows "Deploy failed"

**Solutions**:
```bash
# Check Render logs for errors
# Common issues:
# - Missing environment variables
# - Database connection failures
# - Invalid SECRET_KEY

# Verify environment variables:
# Settings → Environment → Check all required vars are set

# Test database connection:
# Shell → psql "postgresql://..."
```

#### 2. Cold Start Delays

**Symptoms**: First request after idle takes 30-60 seconds

**Solutions**:
- **Expected behavior** on Render free tier
- Service spins down after 15 minutes of inactivity
- Consider upgrading to Starter plan ($7/month) for always-on
- Use UptimeRobot or similar to ping service every 10 minutes (keeps it warm)

#### 3. Database Connection Errors

**Symptoms**: "Could not connect to database" errors

**Solutions**:
```bash
# Check Supabase status
# https://status.supabase.com

# Verify connection string
# Ensure POSTGRES_PASSWORD is correct
# Try connection pooling port (6543) instead of direct (5432)

# Check Supabase logs:
# Dashboard → Logs → Database
```

#### 4. Redis Connection Errors

**Symptoms**: "Failed to connect to Redis" warnings

**Solutions**:
```bash
# Verify Upstash configuration:
# - REDIS_TLS must be "true"
# - REDIS_PASSWORD must be set
# - Use correct host and port from Upstash console

# Test connection:
redis-cli -h <host> -p <port> -a <password> --tls ping
```

### Frontend Issues

#### 1. Build Failures

**Symptoms**: Vercel deployment fails during build

**Solutions**:
```bash
# Check build logs in Vercel dashboard
# Common issues:
# - TypeScript errors
# - Missing dependencies
# - Environment variables not set

# Test build locally:
cd frontend
npm run build

# Clear Vercel cache and redeploy:
# Deployments → ... → Redeploy
```

#### 2. API Connection Errors

**Symptoms**: "Failed to fetch" or CORS errors in browser

**Solutions**:
```bash
# Verify NEXT_PUBLIC_API_URL is correct
# Check browser console for actual error

# Common fixes:
# 1. Update backend CORS origins to include Vercel URL
# 2. Ensure backend is awake (not spun down)
# 3. Check backend health: curl <backend-url>/health
# 4. Verify no trailing slash in NEXT_PUBLIC_API_URL
```

#### 3. Environment Variables Not Applied

**Symptoms**: Old API URL still being used after update

**Solutions**:
- Environment variables are embedded at **build time**
- Must **redeploy** after changing environment variables
- Go to Deployments → Latest → ... → Redeploy
- Clear browser cache if issue persists

### Database Issues

#### 1. Supabase Storage Limit

**Symptoms**: "Storage quota exceeded" errors

**Solutions**:
```bash
# Check database size:
# Supabase Dashboard → Settings → Usage

# Free tier limit: 500MB
# Options:
# 1. Clean up old data
# 2. Archive historical data
# 3. Upgrade to Pro plan ($25/month for 8GB)

# Query to find large tables:
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### 2. MongoDB Atlas Storage Limit

**Symptoms**: "Cluster at storage capacity" warnings

**Solutions**:
- Free tier limit: 512MB
- Monitor usage: Atlas Dashboard → Cluster → Metrics
- Options:
  1. Implement TTL indexes for temporary data
  2. Archive old conversations/searches
  3. Upgrade to M2 ($9/month) or M5 ($25/month)

### Performance Issues

#### 1. Slow Response Times

**Symptoms**: API requests take >2 seconds

**Solutions**:
```bash
# Check if backend is waking from sleep:
# - First request after idle: 30-60s (normal)
# - Subsequent requests should be <500ms

# Enable query logging to find slow queries:
# Supabase → Settings → Database → Query Logs

# Optimize:
# 1. Add database indexes
# 2. Use Redis caching effectively
# 3. Implement pagination
# 4. Consider connection pooling (port 6543)
```

#### 2. Upstash Rate Limits

**Symptoms**: "Rate limit exceeded" errors

**Solutions**:
- Free tier limit: 10,000 commands/day
- Monitor usage: Upstash Console → Database → Metrics
- Options:
  1. Optimize cache usage (increase TTL)
  2. Use conditional caching
  3. Upgrade to pay-as-you-go ($0.20 per 100k commands)

---

## Cost Optimization

### Staying Within Free Tiers

#### Vercel (Frontend)

**Limits**:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ 100 GB-hours serverless function execution
- ✅ 1000 preview deployments

**Tips**:
- Optimize images (use Next.js Image component)
- Enable static page generation where possible
- Minimize serverless function usage
- Monitor bandwidth: Settings → Usage

#### Render (Backend)

**Limits**:
- ✅ 750 hours/month (31.25 days)
- ⚠️ Spins down after 15min idle
- ⚠️ 1 free service per account

**Tips**:
- Run only one environment (dev OR prod) on free tier
- Use paid Starter plan ($7/month) for production if needed
- Consider multiple Render accounts (not recommended)
- Implement efficient caching to reduce compute time

#### Supabase (PostgreSQL)

**Limits**:
- ✅ 500MB database storage
- ✅ Unlimited API requests
- ✅ Up to 2GB bandwidth

**Tips**:
```sql
-- Use efficient data types
-- Good: INTEGER instead of BIGINT when appropriate
-- Good: VARCHAR(255) instead of TEXT when length is known

-- Implement cascading deletes
ALTER TABLE child_table
ADD CONSTRAINT fk_parent
FOREIGN KEY (parent_id) REFERENCES parent_table(id)
ON DELETE CASCADE;

-- Archive old data
-- Example: Archive deals older than 1 year
CREATE TABLE deals_archive AS
SELECT * FROM deals WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM deals WHERE created_at < NOW() - INTERVAL '1 year';
```

#### MongoDB Atlas (Documents)

**Limits**:
- ✅ 512MB storage
- ✅ Shared CPU/RAM

**Tips**:
```javascript
// Implement TTL indexes for temporary data
db.search_history.createIndex(
  { "created_at": 1 },
  { expireAfterSeconds: 2592000 }  // 30 days
);

// Use projection to fetch only needed fields
db.conversations.find(
  { user_id: userId },
  { messages: 0 }  // Exclude large messages array
);

// Compress data where possible
// Store large text as compressed BSON
```

#### Upstash (Redis)

**Limits**:
- ✅ 10,000 commands/day (~7 commands/minute)
- ✅ 256MB storage

**Tips**:
```python
# Use appropriate TTL values
redis.setex("session:user123", 3600, session_data)  # 1 hour

# Batch operations when possible
pipeline = redis.pipeline()
pipeline.set("key1", "value1")
pipeline.set("key2", "value2")
pipeline.execute()

# Monitor command usage
# Upstash Console → Database → Metrics → Commands
```

### Monitoring Usage

#### Set Up Alerts

1. **Supabase**:
   - Dashboard → Settings → Usage
   - Enable email notifications for quota warnings

2. **Upstash**:
   - Console → Database → Alerts
   - Set thresholds (e.g., 80% of daily commands)

3. **Vercel**:
   - Settings → Usage
   - Monitor bandwidth and serverless execution time

4. **Render**:
   - Dashboard → Account → Usage
   - Track billable hours

### When to Upgrade

Consider upgrading when:

1. **Consistent traffic** (>1000 users/day)
2. **Backend needs to be always-on** (upgrade Render to Starter: $7/month)
3. **Database storage exceeds 500MB** (Supabase Pro: $25/month)
4. **Need faster cold starts** (Render Starter: $7/month)
5. **Multiple environments needed** (separate dev/staging/prod)

---

## Custom Domains

### Vercel Custom Domain

1. **Add Domain**:
   - Vercel Dashboard → Settings → Domains
   - Add your domain (e.g., `autodealgenie.com`)

2. **Configure DNS**:
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

3. **SSL Certificate**:
   - Automatically provisioned by Vercel
   - No configuration needed

### Render Custom Domain

1. **Add Domain**:
   - Render Dashboard → Service → Settings → Custom Domain
   - Add your domain (e.g., `api.autodealgenie.com`)

2. **Configure DNS**:
   ```
   Type: CNAME
   Name: api
   Value: <your-service>.onrender.com
   ```

3. **SSL Certificate**:
   - Automatically provisioned by Render
   - Let's Encrypt certificate

4. **Update Frontend**:
   ```bash
   # Vercel environment variable
   NEXT_PUBLIC_API_URL=https://api.autodealgenie.com
   ```

---

## Next Steps

1. ✅ **Set up CI/CD**: Configure GitHub Actions for automated testing
2. ✅ **Add monitoring**: Integrate error tracking (Sentry, LogRocket)
3. ✅ **Implement analytics**: Add Google Analytics or Plausible
4. ✅ **Set up backups**: Configure automated database backups
5. ✅ **Performance testing**: Load test your deployment
6. ✅ **Security audit**: Review security best practices
7. ✅ **Documentation**: Update README with your deployment URLs

---

## Resources

### Official Documentation

- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Upstash Documentation](https://docs.upstash.com)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com)

### Community & Support

- [Vercel Community](https://vercel.com/community)
- [Render Community](https://community.render.com)
- [Supabase Discord](https://discord.supabase.com)
- [AutoDealGenie Issues](https://github.com/Raviteja77/autodealgenie/issues)

### Cost Calculators

- [Vercel Pricing](https://vercel.com/pricing)
- [Render Pricing](https://render.com/pricing)
- [Supabase Pricing](https://supabase.com/pricing)
- [Upstash Pricing](https://upstash.com/pricing)
- [MongoDB Atlas Pricing](https://www.mongodb.com/pricing)

---

## Summary

You now have:

✅ **Frontend** deployed on Vercel with automatic HTTPS and CDN  
✅ **Backend** deployed on Render with auto-scaling  
✅ **Database** on Supabase with connection pooling  
✅ **Cache** on Upstash with TLS support  
✅ **Documents** on MongoDB Atlas  
✅ **Zero monthly costs** (within free tier limits)  
✅ **Separate dev and prod environments**  
✅ **Automatic deployments** from GitHub  

**Total setup time**: ~30-45 minutes

**Monthly cost**: $0 (within free tier) 🎉

Happy deploying! 🚀
