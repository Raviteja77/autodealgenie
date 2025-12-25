# Deployment Guide

Comprehensive guide for deploying AutoDealGenie to production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Database Setup](#database-setup)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [CDN and Static Assets](#cdn-and-static-assets)
8. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
9. [Post-Deployment](#post-deployment)

---

## Pre-Deployment Checklist

### Security

- [ ] Generate strong SECRET_KEY (min 32 characters)
- [ ] Set secure database passwords
- [ ] Configure HTTPS/TLS certificates
- [ ] Enable firewall rules
- [ ] Review CORS allowed origins
- [ ] Set HTTP-only cookies in production
- [ ] Enable security headers
- [ ] Audit dependencies for vulnerabilities
- [ ] Set up secrets management (AWS Secrets Manager, etc.)

### Configuration

- [ ] Set ENVIRONMENT=production
- [ ] Configure production database URLs
- [ ] Set up Redis connection
- [ ] Configure OpenAI API key
- [ ] Set BACKEND_CORS_ORIGINS to production domains
- [ ] Configure email service (if applicable)
- [ ] Set up monitoring and logging
- [ ] Configure backup schedules

### Testing

- [ ] Run full test suite
- [ ] Perform load testing
- [ ] Test database migrations
- [ ] Verify CI/CD pipeline
- [ ] Test rollback procedures

---

## Environment Configuration

### Backend Environment Variables

Create `.env.production`:

```bash
# Environment
ENVIRONMENT=production

# Project Info
PROJECT_NAME=AutoDealGenie API
VERSION=1.0.0
API_V1_STR=/api/v1

# Security - CRITICAL: Use strong random values
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# PostgreSQL
POSTGRES_SERVER=<production-db-host>
POSTGRES_USER=<production-db-user>
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=autodealgenie
POSTGRES_PORT=5432

# MongoDB
MONGODB_URL=mongodb://<user>:<password>@<host>:27017
MONGODB_DB_NAME=autodealgenie

# Redis
REDIS_HOST=<redis-host>
REDIS_PORT=6379
REDIS_DB=0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=<kafka-host>:9092

# OpenAI
OPENAI_API_KEY=<your-api-key>
OPENAI_MODEL=gpt-4

# CORS - Production domains only
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Logging
LOG_LEVEL=INFO

# Mock Services - MUST be false in production
USE_MOCK_SERVICES=false
```

### Frontend Environment Variables

Create `.env.production`:

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NODE_ENV=production
```

### Generate Secrets

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate database password
openssl rand -base64 32

# Generate JWT signing key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Docker Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - ENVIRONMENT=production
    env_file:
      - ./backend/.env.production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - mongodb
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7-jammy
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  mongodb_data:
  redis_data:
```

### Backend Production Dockerfile

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]
```

### Frontend Production Dockerfile

```dockerfile
# frontend/Dockerfile.prod
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

USER nextjs

EXPOSE 3000

ENV NODE_ENV=production

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["npm", "start"]
```

### Deploy with Docker Compose

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

---

## Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autodealgenie

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: autodealgenie-config
  namespace: autodealgenie
data:
  API_V1_STR: "/api/v1"
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: autodealgenie-secrets
  namespace: autodealgenie
type: Opaque
stringData:
  SECRET_KEY: "<generated-secret>"
  POSTGRES_PASSWORD: "<db-password>"
  OPENAI_API_KEY: "<api-key>"
```

### Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autodealgenie-backend
  namespace: autodealgenie
spec:
  replicas: 3
  selector:
    matchLabels:
      app: autodealgenie-backend
  template:
    metadata:
      labels:
        app: autodealgenie-backend
    spec:
      containers:
      - name: backend
        image: your-registry/autodealgenie-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: autodealgenie-secrets
              key: SECRET_KEY
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: autodealgenie-config
              key: ENVIRONMENT
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"

---
apiVersion: v1
kind: Service
metadata:
  name: autodealgenie-backend
  namespace: autodealgenie
spec:
  selector:
    app: autodealgenie-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: autodealgenie-ingress
  namespace: autodealgenie
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    - yourdomain.com
    secretName: autodealgenie-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: autodealgenie-backend
            port:
              number: 8000
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: autodealgenie-frontend
            port:
              number: 3000
```

---

## Database Setup

### PostgreSQL Production Setup

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create backup
docker-compose exec postgres pg_dump -U autodealgenie autodealgenie > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U autodealgenie autodealgenie < backup.sql
```

### MongoDB Setup

```bash
# Create indexes
docker-compose exec mongodb mongosh autodealgenie --eval "
  db.vehicles.createIndex({ 'vin': 1 }, { unique: true });
  db.searches.createIndex({ 'user_id': 1, 'created_at': -1 });
"

# Backup
docker-compose exec mongodb mongodump --out=/backups/$(date +%Y%m%d)

# Restore
docker-compose exec mongodb mongorestore /backups/20251225
```

---

## SSL/TLS Configuration

### Nginx SSL Configuration

```nginx
# nginx/nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Let's Encrypt with Certbot

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal (add to crontab)
0 0 * * * certbot renew --quiet
```

---

## Backup and Disaster Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh - Run daily via cron

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

mkdir -p $BACKUP_DIR

# PostgreSQL backup
docker-compose exec -T postgres pg_dump -U autodealgenie autodealgenie | gzip > $BACKUP_DIR/postgres.sql.gz

# MongoDB backup
docker-compose exec mongodb mongodump --out=$BACKUP_DIR/mongodb

# Redis backup
docker-compose exec redis redis-cli SAVE
docker cp autodealgenie-redis:/data/dump.rdb $BACKUP_DIR/redis.rdb

# Upload to S3
aws s3 sync $BACKUP_DIR s3://your-bucket/backups/$DATE/

# Cleanup old backups (keep last 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} +
```

### Disaster Recovery Plan

1. **Restore Database**: `docker-compose exec -T postgres psql -U autodealgenie < backup.sql`
2. **Restore MongoDB**: `docker-compose exec mongodb mongorestore /backups/latest`
3. **Verify Data Integrity**: Check critical tables and collections
4. **Restart Services**: `docker-compose restart`
5. **Run Health Checks**: Verify all endpoints respond correctly

---

## Post-Deployment

### Smoke Tests

```bash
# Health check
curl https://api.yourdomain.com/health

# Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Test deals endpoint
curl https://api.yourdomain.com/api/v1/deals/ \
  -H "Cookie: access_token=..."
```

### Monitoring Setup

1. Configure Prometheus to scrape metrics
2. Set up Grafana dashboards
3. Configure alerting rules
4. Test alert notifications

### Performance Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Load test
ab -n 1000 -c 10 https://api.yourdomain.com/health
```

---

## Troubleshooting

### Common Issues

**Issue**: Database connection fails
- Check DATABASE_URL is correct
- Verify database is running
- Check firewall rules

**Issue**: CORS errors
- Verify BACKEND_CORS_ORIGINS includes frontend domain
- Check request headers

**Issue**: High memory usage
- Check for memory leaks
- Adjust worker count
- Increase container memory limits

**Issue**: Slow response times
- Check database query performance
- Review Redis cache hit rate
- Enable connection pooling

---

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [AWS ECS](https://aws.amazon.com/ecs/)
- [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform/)
