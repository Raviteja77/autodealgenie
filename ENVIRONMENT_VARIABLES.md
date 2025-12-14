# Environment Variables Documentation

This document provides comprehensive documentation for all environment variables used in the AutoDealGenie application.

## Table of Contents

1. [Backend Environment Variables](#backend-environment-variables)
2. [Frontend Environment Variables](#frontend-environment-variables)
3. [Docker Compose Variables](#docker-compose-variables)
4. [Security Best Practices](#security-best-practices)
5. [Environment-Specific Configurations](#environment-specific-configurations)

---

## Backend Environment Variables

### Required Variables

#### `SECRET_KEY` (Required)
- **Description:** Secret key used for JWT token signing
- **Type:** String
- **Minimum Length:** 32 characters
- **Example:** `your-secret-key-change-this-in-production-min-32-chars`
- **Security:** 🔴 **CRITICAL** - Must be unique and kept secret in production
- **Generation:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

#### `POSTGRES_PASSWORD` (Required)
- **Description:** Password for PostgreSQL database
- **Type:** String
- **Default:** None (must be set)
- **Example:** `autodealgenie_password`
- **Security:** 🔴 **CRITICAL** - Use strong password in production

#### `OPENAI_API_KEY` (Required for AI features)
- **Description:** OpenAI API key for AI-powered insights
- **Type:** String
- **Default:** None
- **Example:** `sk-...`
- **Security:** 🟡 **IMPORTANT** - Keep confidential, monitor usage
- **Get Key:** https://platform.openai.com/api-keys

---

### Database Configuration

#### PostgreSQL

**`POSTGRES_SERVER`**
- **Description:** PostgreSQL server hostname
- **Type:** String
- **Default:** `localhost`
- **Docker:** `postgres` (service name)
- **Example:** `localhost` or `postgres` or `db.example.com`

**`POSTGRES_USER`**
- **Description:** PostgreSQL username
- **Type:** String
- **Default:** `autodealgenie`
- **Example:** `autodealgenie`

**`POSTGRES_DB`**
- **Description:** PostgreSQL database name
- **Type:** String
- **Default:** `autodealgenie`
- **Example:** `autodealgenie` or `autodealgenie_prod`

**`POSTGRES_PORT`**
- **Description:** PostgreSQL port
- **Type:** Integer
- **Default:** `5432`
- **Example:** `5432`

**Generated Variable:**
- `SQLALCHEMY_DATABASE_URI` - Automatically constructed from above variables
- Format: `postgresql://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB}`

#### MongoDB

**`MONGODB_URL`**
- **Description:** MongoDB connection string
- **Type:** String (URI)
- **Default:** `mongodb://localhost:27017`
- **Docker:** `mongodb://mongodb:27017`
- **Example:** `mongodb://user:password@host:27017/database`
- **Format:** `mongodb://[username:password@]host[:port][/database]`

**`MONGODB_DB_NAME`**
- **Description:** MongoDB database name
- **Type:** String
- **Default:** `autodealgenie`
- **Example:** `autodealgenie` or `autodealgenie_prod`

#### Redis

**`REDIS_HOST`**
- **Description:** Redis server hostname
- **Type:** String
- **Default:** `localhost`
- **Docker:** `redis`
- **Example:** `localhost` or `redis` or `cache.example.com`

**`REDIS_PORT`**
- **Description:** Redis server port
- **Type:** Integer
- **Default:** `6379`
- **Example:** `6379`

**`REDIS_DB`**
- **Description:** Redis database number
- **Type:** Integer
- **Default:** `0`
- **Range:** 0-15
- **Example:** `0`

**Generated Variable:**
- `REDIS_URL` - Automatically constructed
- Format: `redis://{HOST}:{PORT}/{DB}`

---

### Message Queue Configuration

#### Kafka

**`KAFKA_BOOTSTRAP_SERVERS`**
- **Description:** Kafka bootstrap servers
- **Type:** String (comma-separated list)
- **Default:** `localhost:9092`
- **Docker:** `kafka:9092`
- **Example:** `localhost:9092` or `kafka1:9092,kafka2:9092,kafka3:9092`

**`KAFKA_CONSUMER_GROUP`**
- **Description:** Kafka consumer group ID
- **Type:** String
- **Default:** `autodealgenie-consumer`
- **Example:** `autodealgenie-consumer` or `autodealgenie-prod-consumer`

**`KAFKA_TOPIC_DEALS`**
- **Description:** Kafka topic for deal events
- **Type:** String
- **Default:** `deals`
- **Example:** `deals` or `prod-deals`

**`KAFKA_TOPIC_NOTIFICATIONS`**
- **Description:** Kafka topic for notification events
- **Type:** String
- **Default:** `notifications`
- **Example:** `notifications` or `prod-notifications`

---

### External API Configuration

#### OpenAI

**`OPENAI_API_KEY`** (Required)
- See [Required Variables](#required-variables) above

**`OPENAI_MODEL`**
- **Description:** OpenAI model to use
- **Type:** String
- **Default:** `gpt-4`
- **Options:** `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Example:** `gpt-4`
- **Cost Consideration:** Different models have different pricing

#### MarketCheck

**`MARKET_CHECK_API_KEY`**
- **Description:** MarketCheck API key for vehicle data
- **Type:** String
- **Default:** None (optional)
- **Example:** `your-marketcheck-api-key-here`
- **Security:** 🟡 **IMPORTANT** - Keep confidential
- **Get Key:** Contact MarketCheck for API access

---

### Security Configuration

**`SECRET_KEY`** (Required)
- See [Required Variables](#required-variables) above

**`ALGORITHM`**
- **Description:** JWT signing algorithm
- **Type:** String
- **Default:** `HS256`
- **Options:** `HS256`, `HS512`
- **Recommendation:** Use `HS256` unless you have specific requirements

**`ACCESS_TOKEN_EXPIRE_MINUTES`**
- **Description:** Access token expiration time
- **Type:** Integer (minutes)
- **Default:** `30`
- **Recommendation:** 15-60 minutes
- **Security Balance:** Shorter = more secure but more frequent refreshes

**`REFRESH_TOKEN_EXPIRE_DAYS`**
- **Description:** Refresh token expiration time
- **Type:** Integer (days)
- **Default:** `7`
- **Recommendation:** 7-30 days
- **Example:** `7` (1 week), `30` (1 month)

**Generated Variables:**
- `ACCESS_TOKEN_EXPIRE_SECONDS` - Auto-calculated
- `REFRESH_TOKEN_EXPIRE_SECONDS` - Auto-calculated

---

### CORS Configuration

**`BACKEND_CORS_ORIGINS`**
- **Description:** Allowed CORS origins (JSON array)
- **Type:** JSON String Array
- **Default:** `["http://localhost:3000","http://localhost:8000"]`
- **Example:** `["http://localhost:3000","https://app.example.com"]`
- **Format:** Must be valid JSON array
- **Security:** Only add trusted origins

---

### Application Configuration

**`PROJECT_NAME`**
- **Description:** Project name for API documentation
- **Type:** String
- **Default:** `AutoDealGenie API`
- **Example:** `AutoDealGenie API`

**`VERSION`**
- **Description:** API version
- **Type:** String
- **Default:** `1.0.0`
- **Example:** `1.0.0`

**`DESCRIPTION`**
- **Description:** API description
- **Type:** String
- **Default:** `AI-powered automotive deal management platform`

**`API_V1_STR`**
- **Description:** API v1 prefix
- **Type:** String
- **Default:** `/api/v1`
- **Example:** `/api/v1` or `/v1`

**`ENVIRONMENT`**
- **Description:** Current environment
- **Type:** String
- **Default:** `development`
- **Options:** `development`, `staging`, `production`
- **Impact:** Affects cookie security settings
- **Example:** `production`

**Generated Variables:**
- `COOKIE_SECURE` - Auto-set to `true` in production, `false` otherwise

---

## Frontend Environment Variables

### Required Variables

**`NEXT_PUBLIC_API_URL`** (Required)
- **Description:** Backend API base URL
- **Type:** String (URL)
- **Default:** `http://localhost:8000`
- **Development:** `http://localhost:8000`
- **Production:** `https://api.yourdomain.com`
- **Note:** Must include protocol (http/https)
- **Example:** `http://localhost:8000` or `https://api.example.com`

**`NEXT_PUBLIC_API_VERSION`**
- **Description:** API version to use
- **Type:** String
- **Default:** `v1`
- **Example:** `v1`
- **Usage:** Appended to API_URL for versioned endpoints

---

## Docker Compose Variables

These variables are used in `docker-compose.yml` and should be set in the root `.env` file.

**`POSTGRES_PASSWORD`** (Required)
- Same as backend POSTGRES_PASSWORD
- Used by both backend and postgres service

**`OPENAI_API_KEY`** (Required)
- Same as backend OPENAI_API_KEY
- Required for AI features to work

---

## Security Best Practices

### 1. Never Commit Secrets

❌ **DON'T:**
```env
# In .env file (committed to git)
SECRET_KEY=my-secret-key-12345
```

✅ **DO:**
```env
# In .env.example (committed to git)
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars

# In .env (NOT committed, in .gitignore)
SECRET_KEY=cDX8kPz9wqY2mNv7fGhJ3xRt6sKuL5aE9bWc4nVm1pQ8hTy0
```

### 2. Use Strong, Random Secrets

**Generate Strong Secrets:**
```bash
# SECRET_KEY (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using openssl
openssl rand -base64 32

# Or using /dev/urandom
head -c 32 /dev/urandom | base64
```

### 3. Different Secrets Per Environment

**Development:**
```env
SECRET_KEY=dev-secret-key-for-testing-only-123456789
```

**Production:**
```env
SECRET_KEY=prod-kPz9wqY2mNv7fGhJ3xRt6sKuL5aE9bWc4nVm1pQ8hTy0
```

### 4. Rotate Secrets Regularly

- **Recommendation:** Rotate production secrets quarterly
- **After Compromise:** Immediately rotate all secrets
- **Process:**
  1. Generate new secret
  2. Update environment variable
  3. Restart application
  4. Invalidate old sessions (if applicable)

### 5. Use Environment-Specific Files

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

### 6. Restrict Access

- Store production secrets in secure secret managers (AWS Secrets Manager, HashiCorp Vault)
- Limit who can access production secrets
- Use IAM roles instead of hardcoded credentials when possible

---

## Environment-Specific Configurations

### Development Environment

**File:** `backend/.env` (local), `frontend/.env.local` (local)

```env
# Backend
SECRET_KEY=dev-secret-key-for-testing-only-123456789
ENVIRONMENT=development
POSTGRES_SERVER=localhost
POSTGRES_USER=autodealgenie
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=autodealgenie_dev
MONGODB_URL=mongodb://localhost:27017
REDIS_HOST=localhost
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
OPENAI_API_KEY=sk-your-dev-key-here
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
```

### Staging Environment

**File:** `.env.staging` (server-side)

```env
# Backend
SECRET_KEY=staging-unique-secret-key-min-32-chars
ENVIRONMENT=staging
POSTGRES_SERVER=staging-db.internal
POSTGRES_USER=autodealgenie_staging
POSTGRES_PASSWORD=strong_staging_password
POSTGRES_DB=autodealgenie_staging
MONGODB_URL=mongodb://staging-mongo.internal:27017
REDIS_HOST=staging-redis.internal
KAFKA_BOOTSTRAP_SERVERS=staging-kafka.internal:9092
OPENAI_API_KEY=sk-your-staging-key-here
BACKEND_CORS_ORIGINS=["https://staging.yourdomain.com"]

# Frontend
NEXT_PUBLIC_API_URL=https://api-staging.yourdomain.com
NEXT_PUBLIC_API_VERSION=v1
```

### Production Environment

**File:** Secret manager (AWS Secrets Manager, etc.)

```env
# Backend
SECRET_KEY=prod-highly-secure-random-key-min-32-chars
ENVIRONMENT=production
POSTGRES_SERVER=prod-db.internal
POSTGRES_USER=autodealgenie_prod
POSTGRES_PASSWORD=very_strong_production_password
POSTGRES_DB=autodealgenie
MONGODB_URL=mongodb://prod-mongo.internal:27017
REDIS_HOST=prod-redis.internal
KAFKA_BOOTSTRAP_SERVERS=prod-kafka-1.internal:9092,prod-kafka-2.internal:9092
OPENAI_API_KEY=sk-your-production-key-here
MARKET_CHECK_API_KEY=your-production-marketcheck-key
BACKEND_CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_API_VERSION=v1
```

---

## Validation and Testing

### Verify Environment Variables

**Backend:**
```bash
cd backend
python -c "from app.core.config import settings; print(f'DB: {settings.SQLALCHEMY_DATABASE_URI}'); print(f'Env: {settings.ENVIRONMENT}')"
```

**Frontend:**
```bash
cd frontend
npm run build
# Check that NEXT_PUBLIC_ variables are accessible
```

### Common Issues

**Issue: Variable not found**
```
KeyError: 'SECRET_KEY'
```
**Solution:** Ensure variable is set in `.env` file

**Issue: Invalid JSON for CORS origins**
```
pydantic.error_wrappers.ValidationError: BACKEND_CORS_ORIGINS
```
**Solution:** Ensure CORS origins is valid JSON array:
```env
# Wrong
BACKEND_CORS_ORIGINS=http://localhost:3000

# Correct
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

**Issue: Frontend can't access API**
```
NetworkError: Failed to fetch
```
**Solution:** Verify `NEXT_PUBLIC_API_URL` is correct and API is running

---

## Migration Checklist

When migrating environments or deploying:

- [ ] Copy `.env.example` to `.env`
- [ ] Update all `REQUIRED` variables
- [ ] Generate new `SECRET_KEY` for environment
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Configure database connection strings
- [ ] Add `OPENAI_API_KEY` if using AI features
- [ ] Update `BACKEND_CORS_ORIGINS` with frontend URL
- [ ] Set `ENVIRONMENT` to correct value
- [ ] Update frontend `NEXT_PUBLIC_API_URL`
- [ ] Test database connectivity
- [ ] Test API connectivity from frontend
- [ ] Verify authentication works
- [ ] Check logs for any missing variables

---

## Support

For issues with environment configuration:
1. Check this documentation
2. Review `.env.example` files
3. Check application logs for specific error messages
4. Verify all required variables are set
5. Ensure variable formats are correct (JSON arrays, URLs, etc.)

---

**Last Updated:** December 14, 2025  
**Version:** 1.0.0
