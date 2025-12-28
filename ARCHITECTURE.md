# AutoDealGenie Deployment Architecture

This document provides a visual overview of the AutoDealGenie deployment architecture for different platforms.

## Free Tier Architecture (Vercel + Render + Supabase)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User's Browser                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 │
                    ┌────────────▼─────────────┐
                    │    Vercel Edge Network   │
                    │    (Global CDN)          │
                    │                          │
                    │  • Next.js 14 Frontend   │
                    │  • Static Site Gen       │
                    │  • Edge Functions        │
                    │  • Auto HTTPS            │
                    └────────────┬─────────────┘
                                 │
                                 │ API Calls
                                 │
                    ┌────────────▼─────────────┐
                    │    Render Web Service    │
                    │    (Oregon Region)       │
                    │                          │
                    │  • FastAPI Backend       │
                    │  • Python 3.11           │
                    │  • Auto-scaling          │
                    │  • Spin down after 15min │
                    └─────┬──────┬──────┬──────┘
                          │      │      │
            ┌─────────────┘      │      └─────────────┐
            │                    │                    │
            │                    │                    │
┌───────────▼──────────┐ ┌──────▼────────┐ ┌────────▼─────────┐
│ Supabase PostgreSQL  │ │ Upstash Redis │ │ MongoDB Atlas    │
│ (Cloud Database)     │ │ (Cloud Cache) │ │ (Cloud NoSQL)    │
│                      │ │               │ │                  │
│ • 500MB Storage      │ │ • 10k cmd/day │ │ • 512MB Storage  │
│ • Connection Pooling │ │ • TLS Required│ │ • M0 Free Tier   │
│ • Auto Backups       │ │ • Global Edge │ │ • Auto Sharding  │
└──────────────────────┘ └───────────────┘ └──────────────────┘
```

## GCP Free Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User's Browser                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 │
        ┌────────────────────────┴────────────────────────┐
        │                                                  │
┌───────▼──────────────┐              ┌──────────────────▼──────────┐
│  Cloud Run Frontend  │              │  Cloud Run Backend          │
│  (us-central1)       │              │  (us-central1)              │
│                      │              │                             │
│  • Next.js SSR       │              │  • FastAPI                  │
│  • Auto-scaling      │              │  • Auto-scaling             │
│  • 2M req/month free │─────────────▶│  • In-memory Cache         │
│  • Container-based   │   API Calls  │  • In-memory Queue         │
└──────────────────────┘              └──────────┬──────────────────┘
                                                 │
                                                 │
                                      ┌──────────▼──────────┐
                                      │ Supabase PostgreSQL │
                                      │ (Cloud Database)    │
                                      │                     │
                                      │ • 500MB Storage     │
                                      │ • Global CDN        │
                                      │ • Auto Backups      │
                                      └─────────────────────┘
```

## Hybrid Architecture (Mix & Match)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User's Browser                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │
        ┌────────────────────────┴────────────────────────┐
        │                                                  │
┌───────▼──────────────┐              ┌──────────────────▼──────────┐
│  Vercel Frontend     │              │  Cloud Run Backend          │
│  (Edge Network)      │              │  (GCP us-central1)          │
│                      │              │                             │
│  • Best CDN          │              │  • Fast cold starts         │
│  • Free unlimited    │              │  • GCP integration         │
└──────────────────────┘              └──────────┬──────────────────┘
                                                 │
                                      ┌──────────┴──────────┐
                                      │                     │
                              ┌───────▼──────────┐  ┌──────▼─────────┐
                              │ Supabase (DB)    │  │ Upstash Redis  │
                              │ • 500MB          │  │ • 10k cmd/day  │
                              └──────────────────┘  └────────────────┘
```

## Deployment Workflow

### Development Flow (dev branch)

```
Developer
    │
    │ git push origin dev
    │
    ├──────────────────┬──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
GitHub           Vercel            Render
dev branch    (Auto Deploy)   (Auto Deploy)
    │                  │                  │
    │                  ▼                  ▼
    │         Preview Deploy     Dev Service
    │         (Unique URL)      (Dev Config)
    │                  │                  │
    │                  └─────────┬────────┘
    │                            │
    ▼                            ▼
Testing                   Test Database
                         (Supabase Dev)
```

### Production Flow (main branch)

```
Developer
    │
    │ PR: dev → main
    │ Review & Approve
    │ git merge
    │
    ├──────────────────┬──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
GitHub           Vercel            Render
main branch   (Auto Deploy)   (Auto Deploy)
    │                  │                  │
    │                  ▼                  ▼
    │         Production       Prod Service
    │      (your-app.vercel.app) (Prod Config)
    │                  │                  │
    │                  └─────────┬────────┘
    │                            │
    ▼                            ▼
Production              Production Database
Release                   (Supabase Prod)
```

## Service Communication

### API Request Flow

```
User Request
     │
     ▼
Vercel CDN (Edge)
     │
     │ Route to API
     ▼
Vercel Edge Function (if applicable)
     │
     │ Forward to Backend
     ▼
Render Backend
     │
     ├─────────┬─────────┬─────────┐
     │         │         │         │
     ▼         ▼         ▼         ▼
  Cache    Database  Documents  AI API
(Upstash)  (Supabase) (MongoDB) (OpenAI)
     │         │         │         │
     └─────────┴─────────┴─────────┘
                 │
                 ▼
           Response Data
                 │
                 ▼
            User Browser
```

### Authentication Flow

```
User Login Request
        │
        ▼
Frontend (Vercel)
        │
        │ POST /api/v1/auth/login
        ▼
Backend (Render)
        │
        ├─ Validate credentials
        │  (Supabase PostgreSQL)
        │
        ├─ Generate JWT tokens
        │  (SECRET_KEY)
        │
        └─ Set HTTP-only cookies
           │
           ▼
    Response with cookies
           │
           ▼
    Frontend stores in cookies
           │
           ▼
    Subsequent requests include cookies
           │
           ▼
    Backend validates JWT
           │
           ▼
    Authorized access
```

## Data Flow

### User Registration

```
1. User submits form
      │
      ▼
2. Frontend validation
      │
      ▼
3. POST /api/v1/auth/signup
      │
      ▼
4. Backend validation
      │
      ▼
5. Hash password (bcrypt)
      │
      ▼
6. Save to PostgreSQL
      │
      ▼
7. Return success
      │
      ▼
8. Auto-login user
```

### Deal Creation with AI

```
1. User enters deal details
      │
      ▼
2. POST /api/v1/deals
      │
      ▼
3. Backend receives data
      │
      ├─────────┬─────────┐
      │         │         │
      ▼         ▼         ▼
4. Save to  Cache in  Generate AI
   PostgreSQL Upstash  evaluation
      │         │      (OpenAI)
      │         │         │
      └─────────┴─────────┘
               │
               ▼
5. Return enriched deal data
               │
               ▼
6. Frontend displays result
```

## Scaling Considerations

### Vertical Scaling (Free → Paid)

```
Free Tier                          Paid Tier
─────────                          ─────────

Render Free (750h/month)    →    Render Starter ($7/month)
• Spins down after 15min         • Always-on
• 512MB RAM                       • 512MB RAM
• Shared CPU                      • Shared CPU
                                  • Faster cold starts

Vercel Free                 →    Vercel Pro ($20/month)
• 100GB bandwidth/month          • 1TB bandwidth/month
• 100 GB-hours functions         • 1000 GB-hours functions

Upstash Free                →    Upstash Paid ($0.20/100k)
• 10k commands/day               • Pay as you go
• 256MB storage                  • Unlimited storage
```

### Horizontal Scaling

```
Current: Single Backend Instance
Future: Multiple Backend Instances

         Load Balancer
               │
     ┌─────────┼─────────┐
     │         │         │
     ▼         ▼         ▼
Backend 1  Backend 2  Backend 3
     │         │         │
     └─────────┴─────────┘
               │
        Shared Database
```

## Security Architecture

```
┌─────────────────────────────────────────────┐
│              Security Layers                │
├─────────────────────────────────────────────┤
│                                             │
│  1. HTTPS/TLS (Automatic)                  │
│     • Vercel: Auto SSL                     │
│     • Render: Auto SSL                     │
│     • Upstash: Required TLS                │
│                                             │
│  2. CORS Protection                        │
│     • Whitelist frontend domains           │
│     • No wildcards in production           │
│                                             │
│  3. Authentication                         │
│     • JWT tokens (HS256)                   │
│     • HTTP-only cookies                    │
│     • Short-lived access tokens (30min)    │
│     • Long-lived refresh tokens (7 days)   │
│                                             │
│  4. Secret Management                      │
│     • Render: Environment variables        │
│     • Vercel: Environment variables        │
│     • No secrets in code                   │
│                                             │
│  5. Database Security                      │
│     • Supabase: Built-in auth              │
│     • MongoDB Atlas: IP whitelist          │
│     • Upstash: Password + TLS              │
│                                             │
│  6. Rate Limiting                          │
│     • Redis-based rate limiter             │
│     • Per-user and per-IP limits           │
│                                             │
└─────────────────────────────────────────────┘
```

## Disaster Recovery

```
┌─────────────────────────────────────────────┐
│           Backup & Recovery Plan            │
├─────────────────────────────────────────────┤
│                                             │
│  Supabase PostgreSQL:                       │
│  • Automatic backups (daily)                │
│  • Point-in-time recovery (7 days)          │
│  • Manual export: pg_dump                   │
│                                             │
│  MongoDB Atlas:                             │
│  • Automatic backups (continuous)           │
│  • Point-in-time recovery                   │
│  • Manual export: mongodump                 │
│                                             │
│  Upstash Redis:                             │
│  • Ephemeral cache (no backups needed)      │
│  • Can be rebuilt from database             │
│                                             │
│  Application Code:                          │
│  • Git repository (GitHub)                  │
│  • Multiple branches (dev, main)            │
│  • Easy rollback via Vercel/Render          │
│                                             │
│  Recovery Time Objective (RTO): < 1 hour    │
│  Recovery Point Objective (RPO): < 1 day    │
│                                             │
└─────────────────────────────────────────────┘
```

## Cost Monitoring

```
Service          Free Limit          Alert Threshold    Action
─────────────────────────────────────────────────────────────────
Vercel           100GB bandwidth     80GB              Monitor
Render           750 hours           600 hours         Consider paid
Supabase         500MB database      400MB             Archive data
Upstash          10k cmds/day        8k commands       Optimize cache
MongoDB Atlas    512MB storage       400MB             Cleanup old data
```

## Performance Metrics

```
Metric                   Target          Free Tier Actual
────────────────────────────────────────────────────────────
Frontend Load Time       < 2s            ~1.5s (Vercel CDN)
Backend Cold Start       < 10s           ~30-60s (Render)
Backend Warm Response    < 500ms         ~200-400ms
Database Query           < 100ms         ~50-100ms (Supabase)
Redis Cache Hit          > 80%           Varies
API Availability         > 99%           ~95% (cold starts)
```

---

## Legend

```
┌─────┐
│ Box │  = Service/Component
└─────┘

  │     = Connection/Flow
  ▼     = Direction of flow
  ─     = Relationship
```

---

**Last Updated**: 2024-12-28  
**Version**: 1.0.0  
**Maintainer**: AutoDealGenie Team
