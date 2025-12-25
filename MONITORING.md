# Monitoring and Observability Guide

Comprehensive guide for monitoring AutoDealGenie application in production with Prometheus and Grafana.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Metrics](#metrics)
5. [Alerting](#alerting)
6. [Dashboards](#dashboards)
7. [Runbooks](#runbooks)
8. [On-Call Procedures](#on-call-procedures)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## Overview

AutoDealGenie uses a comprehensive monitoring stack based on industry-standard tools:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notification management
- **Exporters**: PostgreSQL and Redis metrics exporters

### Key Features

- Real-time application and infrastructure metrics
- Pre-configured dashboards for different use cases
- Intelligent alerting with customizable thresholds
- Business metrics tracking (deals, users, authentication)
- Database performance monitoring
- Cache performance tracking

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- AutoDealGenie application running

### Starting the Monitoring Stack

1. **Start all services including monitoring**:
   ```bash
   docker-compose up -d
   ```

2. **Access monitoring services**:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001 (admin/admin)
   - Alertmanager: http://localhost:9093
   - Backend Metrics: http://localhost:8000/metrics

3. **Verify services are running**:
   ```bash
   docker-compose ps
   ```

4. **Check Prometheus targets**:
   - Navigate to http://localhost:9090/targets
   - All targets should show "UP" status

5. **Access Grafana dashboards**:
   - Login to Grafana at http://localhost:3001
   - Navigate to Dashboards → Browse
   - Open pre-configured dashboards in "AutoDealGenie" folder

### Initial Configuration

The monitoring stack comes pre-configured with:
- ✅ Prometheus datasource
- ✅ 3 pre-built dashboards
- ✅ Alert rules for critical scenarios
- ✅ Database exporters for PostgreSQL and Redis

---

## Architecture

### Component Overview

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   FastAPI   │─────▶│ Prometheus  │─────▶│   Grafana    │
│   Backend   │      │  (Metrics)  │      │ (Dashboards) │
└─────────────┘      └─────────────┘      └──────────────┘
      │                     │
      │                     ▼
      │              ┌─────────────┐
      │              │Alertmanager │
      │              │  (Alerts)   │
      │              └─────────────┘
      │
      ├──────────────────────┐
      ▼                      ▼
┌─────────────┐      ┌─────────────┐
│  Postgres   │      │    Redis    │
│  Exporter   │      │  Exporter   │
└─────────────┘      └─────────────┘
```

### Data Flow

1. **Metrics Collection**:
   - FastAPI app exposes metrics at `/metrics` endpoint
   - Prometheus scrapes metrics every 15 seconds
   - Database exporters provide DB-specific metrics

2. **Visualization**:
   - Grafana queries Prometheus for metrics data
   - Pre-built dashboards provide instant insights
   - Custom queries can be created as needed

3. **Alerting**:
   - Prometheus evaluates alert rules every 30 seconds
   - Firing alerts are sent to Alertmanager
   - Alertmanager routes alerts based on severity and component

---

## Metrics

### Prometheus Setup

**Docker Compose Configuration:**

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'

volumes:
  prometheus_data:
```

**Prometheus Configuration (prometheus.yml):**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'autodealgenie-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### FastAPI Metrics Instrumentation

Add Prometheus middleware to FastAPI:

```python
# backend/requirements.txt
prometheus-fastapi-instrumentator==7.0.0

# backend/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)
```

## Metrics

### Overview

AutoDealGenie collects comprehensive metrics across multiple layers:

- **Application Metrics**: HTTP requests, latencies, error rates
- **Business Metrics**: Deals, user signups, authentication events
- **Database Metrics**: Connection pools, query performance, transactions
- **Cache Metrics**: Hit rates, memory usage, operations
- **External API Metrics**: Third-party API calls and performance
- **LLM Metrics**: AI model usage, tokens, and performance

### Available Metrics

#### HTTP Metrics (Auto-instrumented)

Automatically collected by `prometheus-fastapi-instrumentator`:

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, status, handler |
| `http_request_duration_seconds` | Histogram | Request latency in seconds (p50, p90, p95, p99) |
| `http_request_size_bytes` | Summary | Request body size |
| `http_response_size_bytes` | Summary | Response body size |
| `autodealgenie_requests_inprogress` | Gauge | Number of requests currently being processed |

#### Business Metrics

Custom metrics defined in `app/metrics/prometheus.py`:

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `autodealgenie_deals_created_total` | Counter | Total deals created | status |
| `autodealgenie_user_signups_total` | Counter | Total user registrations | - |
| `autodealgenie_auth_success_total` | Counter | Successful authentications | - |
| `autodealgenie_auth_failures_total` | Counter | Failed authentication attempts | - |
| `autodealgenie_vehicle_searches_total` | Counter | Vehicle searches performed | search_type |
| `autodealgenie_vehicle_search_duration_seconds` | Histogram | Search processing time | - |
| `autodealgenie_negotiation_sessions_total` | Counter | Negotiation sessions started | - |
| `autodealgenie_negotiation_messages_total` | Counter | Messages exchanged | role |

#### Database Metrics

PostgreSQL metrics from `postgres-exporter`:

| Metric | Type | Description |
|--------|------|-------------|
| `pg_stat_database_numbackends` | Gauge | Active database connections |
| `pg_settings_max_connections` | Gauge | Maximum allowed connections |
| `pg_stat_database_xact_commit` | Counter | Committed transactions |
| `pg_stat_database_xact_rollback` | Counter | Rolled back transactions |
| `pg_stat_database_tup_inserted` | Counter | Rows inserted |
| `pg_stat_database_tup_updated` | Counter | Rows updated |
| `pg_stat_database_tup_deleted` | Counter | Rows deleted |

#### Cache Metrics

Redis metrics from `redis-exporter`:

| Metric | Type | Description |
|--------|------|-------------|
| `redis_memory_used_bytes` | Gauge | Memory used by Redis |
| `redis_memory_max_bytes` | Gauge | Maximum memory limit |
| `redis_connected_clients` | Gauge | Number of connected clients |
| `redis_keyspace_hits_total` | Counter | Successful key lookups |
| `redis_keyspace_misses_total` | Counter | Failed key lookups |
| `redis_commands_processed_total` | Counter | Total commands processed |

### Using Metrics in Code

#### Example 1: Track Deal Creation

```python
from app.metrics import deals_created, loan_processing_duration

@router.post("/api/v1/deals/")
async def create_deal(deal: DealCreate, user: User = Depends(get_current_user)):
    """Create a new deal and track metrics"""
    
    # Create the deal
    new_deal = await deal_service.create(deal, user.id)
    
    # Increment the counter with status label
    deals_created.labels(status=new_deal.status).inc()
    
    return new_deal
```

#### Example 2: Track API Latency

```python
from app.metrics import vehicle_search_duration

@router.post("/api/v1/search/")
async def search_vehicles(criteria: SearchCriteria):
    """Search for vehicles and track performance"""
    
    # Track search duration
    with vehicle_search_duration.time():
        results = await vehicle_service.search(criteria)
    
    return results
```

#### Example 3: Track Authentication

```python
from app.metrics import auth_success, auth_failures

@router.post("/api/v1/auth/login")
async def login(credentials: LoginCredentials):
    """Login endpoint with authentication metrics"""
    
    try:
        user = await auth_service.authenticate(credentials)
        auth_success.inc()
        return {"token": create_token(user)}
    except InvalidCredentials:
        auth_failures.inc()
        raise HTTPException(401, "Invalid credentials")
```

#### Example 4: Track Database Queries

```python
from app.metrics import db_query_duration, db_queries_total, db_query_errors

async def get_deal(deal_id: int):
    """Get deal with query metrics"""
    
    # Track query
    db_queries_total.labels(operation="select", table="deals").inc()
    
    try:
        with db_query_duration.labels(operation="select", table="deals").time():
            deal = await db.query(Deal).filter(Deal.id == deal_id).first()
        return deal
    except Exception as e:
        db_query_errors.labels(operation="select", table="deals").inc()
        raise
```

### Accessing Metrics

1. **Raw Metrics Endpoint**:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Prometheus Query UI**:
   - Navigate to http://localhost:9090
   - Use PromQL to query metrics

3. **Grafana Dashboards**:
   - Pre-built dashboards at http://localhost:3001
   - Create custom queries and visualizations

### Common PromQL Queries

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Error rate percentage
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Cache hit rate
rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))

# Database connection pool utilization
pg_stat_database_numbackends / pg_settings_max_connections * 100

# Deals created in last hour
increase(autodealgenie_deals_created_total[1h])
```

---

## Alerting

### Alert Rules

AutoDealGenie includes pre-configured alert rules in `monitoring/prometheus/alerts.yml`:

#### Critical Alerts

| Alert | Condition | Duration | Description |
|-------|-----------|----------|-------------|
| **ServiceDown** | Backend unreachable | 2 minutes | Backend service is not responding |
| **HighErrorRate** | 5xx errors > 5% | 5 minutes | High percentage of server errors |
| **DatabaseDown** | PostgreSQL unreachable | 2 minutes | Database is not accessible |
| **RedisDown** | Redis unreachable | 2 minutes | Cache service is down |
| **DiskSpaceLow** | < 10% disk space | 5 minutes | Running out of disk space |

#### Warning Alerts

| Alert | Condition | Duration | Description |
|-------|-----------|----------|-------------|
| **HighAPILatency** | p95 > 2 seconds | 10 minutes | API response time is slow |
| **HighRequestRate** | > 100 req/s | 10 minutes | Unusually high traffic |
| **DatabaseConnectionPoolHigh** | > 80% utilization | 5 minutes | Connection pool nearly full |
| **LowCacheHitRate** | < 80% hit rate | 15 minutes | Cache not performing well |
| **HighRedisMemoryUsage** | > 90% memory | 5 minutes | Redis running out of memory |
| **SlowQueries** | Avg time > 1s | 10 minutes | Database queries are slow |

#### Info Alerts

| Alert | Condition | Duration | Description |
|-------|-----------|----------|-------------|
| **LowUserSignupRate** | < 0.01/hour | 2 hours | Signup rate is low |
| **HighAuthenticationFailureRate** | > 5 failures/s | 10 minutes | Many auth failures |

### Alert Routing

Alertmanager routes alerts based on severity and component:

```yaml
# Critical alerts → PagerDuty (on-call team)
severity: critical → pagerduty (immediate)

# Warning alerts → Slack (team channel)
severity: warning → slack (within 1 hour)

# Info alerts → Slack (low priority)
severity: info → slack (daily digest)

# Component-specific routing
component: database → dba-team
component: security → security-team
```

### Configuring Notifications

#### Slack Integration

1. Create a Slack webhook URL:
   - Go to https://api.slack.com/apps
   - Create a new app → Incoming Webhooks
   - Add webhook to your workspace
   - Copy the webhook URL

2. Update `monitoring/alertmanager/alertmanager.yml`:
   ```yaml
   global:
     slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
   
   receivers:
     - name: 'critical-alerts'
       slack_configs:
         - channel: '#critical-alerts'
           title: ':rotating_light: CRITICAL: {{ .GroupLabels.alertname }}'
           text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}'
           send_resolved: true
   ```

3. Restart Alertmanager:
   ```bash
   docker-compose restart alertmanager
   ```

#### PagerDuty Integration

1. Get PagerDuty service integration key:
   - Log into PagerDuty
   - Go to Services → Select service → Integrations
   - Add integration → Prometheus
   - Copy the integration key

2. Update `monitoring/alertmanager/alertmanager.yml`:
   ```yaml
   receivers:
     - name: 'critical-alerts'
       pagerduty_configs:
         - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
           description: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
   ```

#### Email Notifications

1. Configure SMTP settings in `monitoring/alertmanager/alertmanager.yml`:
   ```yaml
   global:
     smtp_smarthost: 'smtp.gmail.com:587'
     smtp_from: 'alerts@autodealgenie.com'
     smtp_auth_username: 'alerts@autodealgenie.com'
     smtp_auth_password: 'your-app-password'
   
   receivers:
     - name: 'database-alerts'
       email_configs:
         - to: 'dba-team@autodealgenie.com'
           subject: 'Database Alert: {{ .GroupLabels.alertname }}'
   ```

### Alert Silencing

Temporarily silence alerts during maintenance:

```bash
# Silence all alerts for 1 hour
amtool silence add alertname=~".+" --duration=1h --author="ops-team" --comment="Planned maintenance"

# Silence specific alert
amtool silence add alertname="HighErrorRate" --duration=30m --author="john" --comment="Deploying fix"

# List active silences
amtool silence query

# Expire a silence
amtool silence expire <silence-id>
```

---

## Dashboards

### Pre-configured Dashboards

AutoDealGenie includes three pre-built Grafana dashboards:

#### 1. System Overview Dashboard

**Purpose**: Real-time application health and performance monitoring

**Panels**:
- Request Rate (requests/second by endpoint)
- Error Rate (5xx percentage gauge)
- API Latency Percentiles (p50, p90, p95, p99)
- HTTP Status Codes distribution
- PostgreSQL Active Connections
- Redis Memory Usage
- Application Memory Usage

**Use Cases**:
- Quick health check
- Incident investigation
- Performance monitoring
- Capacity planning

**Access**: Grafana → Dashboards → System Overview

#### 2. Business Metrics Dashboard

**Purpose**: Track business KPIs and user activity

**Panels**:
- Deals Created per Hour (by status)
- User Signups per Hour
- Authentication Success Rate
- Total Deals (24h summary)
- Top API Endpoints by Usage (pie chart)
- Authentication Failures trend
- Deals by Status table

**Use Cases**:
- Business reporting
- User activity monitoring
- Feature usage analysis
- Growth tracking

**Access**: Grafana → Dashboards → Business Metrics

#### 3. Database Performance Dashboard

**Purpose**: Monitor database and cache health

**Panels**:
- PostgreSQL Connection Pool utilization
- Database Transactions (commits/rollbacks)
- Database Operations (inserts/updates/deletes)
- Redis Memory Usage vs Max Memory
- Redis Cache Hit Rate
- Redis Commands per Second
- Redis Connected Clients

**Use Cases**:
- Database performance tuning
- Query optimization
- Capacity planning
- Cache efficiency analysis

**Access**: Grafana → Dashboards → Database Performance

### Creating Custom Dashboards

1. **Access Grafana**:
   ```
   http://localhost:3001
   Username: admin
   Password: admin
   ```

2. **Create new dashboard**:
   - Click "+" → Dashboard
   - Add new panel
   - Select Prometheus datasource

3. **Example: Create uptime panel**:
   ```promql
   # Query
   up{job="autodealgenie-backend"}
   
   # Visualization: Stat
   # Display: Last value
   # Thresholds: 0 (red), 1 (green)
   ```

4. **Export dashboard**:
   - Save dashboard
   - Dashboard settings → JSON Model
   - Copy JSON to `monitoring/grafana/dashboards/`

### Dashboard Best Practices

1. **Use consistent time ranges**: Default to 1h, provide 5m, 15m, 6h, 24h options
2. **Set appropriate refresh rates**: 10s for operational, 30s for business metrics
3. **Use meaningful colors**: Green (good), Yellow (warning), Red (critical)
4. **Add annotations**: Mark deployments, incidents, maintenance windows
5. **Include descriptions**: Add panel descriptions for context
6. **Use variables**: Create reusable dashboards with template variables

---

## Runbooks

### ServiceDown Alert

**Severity**: Critical  
**Impact**: Users cannot access the application

#### Symptoms
- Users report application is unavailable
- Health checks failing
- HTTP 503 or connection refused errors

#### Investigation Steps

1. **Check service status**:
   ```bash
   docker-compose ps autodealgenie-backend
   ```

2. **Check application logs**:
   ```bash
   docker logs autodealgenie-backend --tail 100
   ```

3. **Check resource usage**:
   ```bash
   docker stats autodealgenie-backend
   ```

4. **Check dependencies**:
   ```bash
   # PostgreSQL
   docker exec autodealgenie-postgres pg_isready
   
   # MongoDB
   docker exec autodealgenie-mongodb mongosh --eval "db.adminCommand('ping')"
   
   # Redis
   docker exec autodealgenie-redis redis-cli ping
   ```

#### Resolution Steps

1. **Restart the backend service**:
   ```bash
   docker-compose restart backend
   ```

2. **If restart fails, check for crashes**:
   ```bash
   docker logs autodealgenie-backend --tail 200
   ```

3. **Common issues**:
   - Database connection failure → Check database service
   - Out of memory → Increase container memory limit
   - Port conflict → Check if port 8000 is in use
   - Configuration error → Validate environment variables

4. **Escalate if issue persists**:
   - Notify senior engineer
   - Check for infrastructure issues
   - Consider rolling back recent deployments

---

### HighErrorRate Alert

**Severity**: Critical  
**Impact**: Application returning many 5xx errors

#### Symptoms
- Error rate > 5% for 5 minutes
- Users experiencing failures
- Logs showing exceptions

#### Investigation Steps

1. **Identify error patterns**:
   ```promql
   # Top error endpoints
   topk(5, rate(http_requests_total{status=~"5.."}[5m]))
   ```

2. **Check application logs**:
   ```bash
   docker logs autodealgenie-backend --tail 100 | grep ERROR
   ```

3. **Check external dependencies**:
   - Database connectivity
   - Redis availability
   - External API status
   - Kafka connectivity

#### Resolution Steps

1. **Database issues**:
   ```bash
   # Check connection pool
   docker exec autodealgenie-postgres psql -U autodealgenie -c "SELECT count(*) FROM pg_stat_activity;"
   
   # Restart if needed
   docker-compose restart postgres
   ```

2. **External API failures**:
   - Check OpenRouter API status
   - Verify API keys are valid
   - Check rate limits

3. **Application errors**:
   - Review recent code changes
   - Check for memory leaks
   - Validate configuration

4. **Temporary mitigation**:
   ```bash
   # Restart backend to clear transient errors
   docker-compose restart backend
   ```

---

### HighAPILatency Alert

**Severity**: Warning  
**Impact**: Slow user experience

#### Symptoms
- p95 latency > 2 seconds for 10 minutes
- Users report slow loading
- Timeouts occurring

#### Investigation Steps

1. **Identify slow endpoints**:
   ```promql
   # Slowest endpoints
   topk(5, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))
   ```

2. **Check database query performance**:
   ```sql
   -- Connect to database
   docker exec -it autodealgenie-postgres psql -U autodealgenie
   
   -- Check slow queries
   SELECT query, mean_exec_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_exec_time DESC 
   LIMIT 10;
   ```

3. **Check cache hit rate**:
   ```promql
   rate(redis_keyspace_hits_total[5m]) / (rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
   ```

4. **Check resource utilization**:
   ```bash
   docker stats
   ```

#### Resolution Steps

1. **Database optimization**:
   - Add missing indexes
   - Optimize slow queries
   - Increase connection pool size

2. **Cache warming**:
   ```bash
   # Warm up cache for common queries
   curl http://localhost:8000/api/v1/vehicles?make=Toyota
   ```

3. **External API issues**:
   - Check external API latency
   - Implement caching for external calls
   - Add request timeouts

4. **Scale resources**:
   - Increase backend replicas
   - Add more database connections
   - Increase memory allocation

---

### DatabaseConnectionPoolHigh Alert

**Severity**: Warning  
**Impact**: Risk of connection exhaustion

#### Symptoms
- Connection pool > 80% utilized for 5 minutes
- New requests may fail to get database connections
- Increased latency

#### Investigation Steps

1. **Check active connections**:
   ```sql
   SELECT count(*) as active_connections, 
          state, 
          wait_event_type, 
          wait_event
   FROM pg_stat_activity
   WHERE datname = 'autodealgenie'
   GROUP BY state, wait_event_type, wait_event
   ORDER BY active_connections DESC;
   ```

2. **Identify long-running queries**:
   ```sql
   SELECT pid, 
          now() - query_start AS duration, 
          state, 
          query
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY duration DESC;
   ```

3. **Check for connection leaks**:
   ```bash
   # Monitor connection count over time
   watch -n 1 'docker exec autodealgenie-postgres psql -U autodealgenie -c "SELECT count(*) FROM pg_stat_activity WHERE datname = '\''autodealgenie'\'';"'
   ```

#### Resolution Steps

1. **Kill long-running queries** (if safe):
   ```sql
   -- Terminate specific query
   SELECT pg_terminate_backend(<pid>);
   ```

2. **Increase connection pool size**:
   ```yaml
   # In backend environment
   DB_POOL_SIZE: 20  # Increase from default
   DB_MAX_OVERFLOW: 10
   ```

3. **Fix connection leaks**:
   - Review code for unclosed connections
   - Ensure proper session cleanup
   - Use context managers for database sessions

4. **Restart backend** (last resort):
   ```bash
   docker-compose restart backend
   ```

---

### LowCacheHitRate Alert

**Severity**: Warning  
**Impact**: Increased database load and latency

#### Symptoms
- Cache hit rate < 80% for 15 minutes
- Increased database queries
- Higher latency

#### Investigation Steps

1. **Check cache statistics**:
   ```bash
   docker exec autodealgenie-redis redis-cli INFO stats
   ```

2. **Analyze key patterns**:
   ```bash
   # Check key count
   docker exec autodealgenie-redis redis-cli DBSIZE
   
   # Sample keys
   docker exec autodealgenie-redis redis-cli KEYS "*" | head -20
   ```

3. **Check memory usage**:
   ```bash
   docker exec autodealgenie-redis redis-cli INFO memory
   ```

#### Resolution Steps

1. **Warm up cache**:
   ```python
   # Run cache warming script
   python scripts/warm_cache.py
   ```

2. **Adjust TTL values**:
   - Increase TTL for frequently accessed data
   - Review cache invalidation strategy

3. **Increase cache size**:
   ```yaml
   # docker-compose.yml
   redis:
     command: redis-server --maxmemory 512mb
   ```

4. **Optimize cache keys**:
   - Review key naming strategy
   - Implement cache prefetching
   - Use cache-aside pattern properly

---

## On-Call Procedures

### On-Call Schedule

- **Primary On-Call**: Responds to critical alerts immediately
- **Secondary On-Call**: Backup for primary, responds if no acknowledgment within 15 minutes
- **Escalation**: Engineering manager after 30 minutes

### Alert Response Times

| Severity | Response Time | Resolution Time |
|----------|--------------|-----------------|
| Critical | 5 minutes | 1 hour |
| Warning | 30 minutes | 4 hours |
| Info | Next business day | 1 week |

### On-Call Responsibilities

1. **Acknowledge alerts** within SLA
2. **Investigate and diagnose** issues using runbooks
3. **Resolve or mitigate** the problem
4. **Document** incident in post-mortem
5. **Update runbooks** if new issues discovered

### Communication Protocol

1. **Alert fired** → Acknowledge in PagerDuty/Slack
2. **Investigating** → Post status update in #incidents channel
3. **Mitigation** → Communicate workaround to users
4. **Resolution** → Post resolution update
5. **Post-mortem** → Schedule within 48 hours

### Escalation Path

```
Alert → On-Call Engineer (Primary)
  ↓ (15 min no ack)
On-Call Engineer (Secondary)
  ↓ (30 min no resolution)
Engineering Manager
  ↓ (1 hour no resolution)
CTO
```

### Tools Access

Ensure on-call engineer has access to:
- [ ] Grafana dashboards
- [ ] Prometheus/Alertmanager UI
- [ ] Application logs (Docker/Cloud)
- [ ] Database access (read-only recommended)
- [ ] PagerDuty/Slack notifications
- [ ] Production environment (SSH/kubectl)
- [ ] AWS Console (if using cloud)

### After Hours Support

1. **Non-critical alerts**: Can wait until next business day
2. **Critical alerts**: Follow escalation immediately
3. **Maintenance windows**: Schedule during low-traffic periods
4. **Deployments**: Avoid Fridays and weekends

---

## Testing

### Testing Locally

#### 1. Start Monitoring Stack

```bash
# Start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Expected output: All services should be "Up" with healthy status
```

#### 2. Verify Prometheus is Scraping Metrics

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# All jobs should show "up" status
```

#### 3. Test Metrics Collection

```bash
# Generate some traffic
for i in {1..100}; do
  curl http://localhost:8000/health
  curl http://localhost:8000/api/v1/deals
done

# Check metrics are being recorded
curl http://localhost:8000/metrics | grep http_requests_total

# Expected: Counter should increase
```

#### 4. Test Custom Metrics

```python
# Test script: test_metrics.py
import requests
import time

# Create a deal (increment business metric)
response = requests.post(
    "http://localhost:8000/api/v1/deals/",
    json={"vehicle_id": 1, "asking_price": 25000},
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

# Wait for Prometheus to scrape
time.sleep(15)

# Verify metric increased
metrics = requests.get("http://localhost:8000/metrics").text
assert "autodealgenie_deals_created_total" in metrics
print("✓ Custom metrics working")
```

#### 5. Test Grafana Dashboards

1. Access Grafana: http://localhost:3001
2. Login with admin/admin
3. Navigate to Dashboards → Browse
4. Open each dashboard and verify:
   - Data is loading (no "No data" errors)
   - Time series show recent data
   - Gauges and stats display values

#### 6. Test Alert Rules

```bash
# Simulate high error rate
for i in {1..100}; do
  curl http://localhost:8000/nonexistent-endpoint
done

# Wait 5 minutes and check Prometheus alerts
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {alert: .labels.alertname, state: .state}'

# Check Alertmanager
curl http://localhost:9093/api/v2/alerts | jq '.[] | {alertname: .labels.alertname, status: .status.state}'
```

### Testing in Staging

#### Pre-Deployment Checklist

- [ ] Prometheus targets are configured
- [ ] Alert rules are loaded
- [ ] Grafana datasource is connected
- [ ] Dashboards are imported
- [ ] Notification channels are configured
- [ ] Alert silences are removed

#### Test Alert Flow

1. **Trigger a test alert**:
   ```bash
   # Manually create a test alert
   cat <<EOF | curl --data-binary @- http://localhost:9093/api/v1/alerts
   [
     {
       "labels": {
         "alertname": "TestAlert",
         "severity": "warning"
       },
       "annotations": {
         "summary": "This is a test alert"
       }
     }
   ]
   EOF
   ```

2. **Verify notification received**:
   - Check Slack channel for alert
   - Check PagerDuty for page
   - Verify email received

3. **Acknowledge and resolve**:
   - Acknowledge in notification system
   - Verify alert clears in Prometheus

#### Load Testing

```bash
# Install artillery for load testing
npm install -g artillery

# Create load test config: artillery-config.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 300
      arrivalRate: 10
      name: "Sustained load"
scenarios:
  - name: "API endpoints"
    flow:
      - get:
          url: "/health"
      - get:
          url: "/api/v1/deals"
      - post:
          url: "/api/v1/search"
          json:
            make: "Toyota"

# Run load test
artillery run artillery-config.yml

# Monitor metrics during load test
# - Watch request rate increase
# - Monitor latency percentiles
# - Check for any alerts firing
```

### Automated Testing

#### Unit Tests for Metrics

```python
# tests/test_metrics.py
import pytest
from app.metrics import deals_created, user_signups

def test_deals_created_metric():
    """Test deals_created counter increments"""
    initial = deals_created.labels(status="pending")._value.get()
    deals_created.labels(status="pending").inc()
    assert deals_created.labels(status="pending")._value.get() == initial + 1

def test_user_signups_metric():
    """Test user_signups counter increments"""
    initial = user_signups._value.get()
    user_signups.inc()
    assert user_signups._value.get() == initial + 1
```

#### Integration Tests

```python
# tests/integration/test_metrics_endpoint.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_metrics_endpoint(async_client: AsyncClient):
    """Test /metrics endpoint returns Prometheus format"""
    response = await async_client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "autodealgenie_deals_created_total" in response.text

@pytest.mark.asyncio
async def test_metrics_increment(async_client: AsyncClient):
    """Test metrics increment on API calls"""
    # Get initial metric value
    response1 = await async_client.get("/metrics")
    initial_requests = parse_metric(response1.text, "http_requests_total")
    
    # Make API call
    await async_client.get("/health")
    
    # Verify metric incremented
    response2 = await async_client.get("/metrics")
    new_requests = parse_metric(response2.text, "http_requests_total")
    assert new_requests > initial_requests
```

#### CI/CD Integration

```yaml
# .github/workflows/monitoring-tests.yml
name: Monitoring Tests

on: [push, pull_request]

jobs:
  test-metrics:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Wait for services
        run: |
          timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
          timeout 60 bash -c 'until curl -f http://localhost:9090/-/healthy; do sleep 2; done'
      
      - name: Test Prometheus targets
        run: |
          curl http://localhost:9090/api/v1/targets | jq -e '.data.activeTargets[].health == "up"'
      
      - name: Test metrics endpoint
        run: |
          curl http://localhost:8000/metrics | grep -q "http_requests_total"
      
      - name: Test alert rules
        run: |
          curl http://localhost:9090/api/v1/rules | jq -e '.data.groups | length > 0'
      
      - name: Cleanup
        run: docker-compose down
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Prometheus Cannot Scrape Metrics

**Symptoms**:
- Prometheus targets show "DOWN" status
- Error: "context deadline exceeded"
- No data in Grafana dashboards

**Solutions**:

1. **Check backend is running**:
   ```bash
   docker-compose ps backend
   curl http://localhost:8000/health
   ```

2. **Verify metrics endpoint is accessible**:
   ```bash
   curl http://localhost:8000/metrics
   ```

3. **Check Prometheus configuration**:
   ```bash
   # View Prometheus config
   docker exec autodealgenie-prometheus cat /etc/prometheus/prometheus.yml
   
   # Reload config
   curl -X POST http://localhost:9090/-/reload
   ```

4. **Check network connectivity**:
   ```bash
   # From Prometheus container
   docker exec autodealgenie-prometheus wget -qO- http://backend:8000/metrics
   ```

5. **Check logs**:
   ```bash
   docker logs autodealgenie-prometheus --tail 50
   ```

#### Issue 2: Grafana Shows "No Data"

**Symptoms**:
- Dashboards load but show "No data"
- Queries return empty results

**Solutions**:

1. **Verify Prometheus datasource**:
   - Grafana → Configuration → Data Sources
   - Click Prometheus → Test
   - Should show "Data source is working"

2. **Check Prometheus has data**:
   ```bash
   # Query Prometheus directly
   curl 'http://localhost:9090/api/v1/query?query=up' | jq
   ```

3. **Verify time range**:
   - Check dashboard time range (top right)
   - Set to "Last 1 hour" or "Last 15 minutes"

4. **Test query in Prometheus**:
   - Go to http://localhost:9090
   - Try the same query from Grafana
   - Verify it returns data

5. **Check metric names**:
   ```bash
   # List all metrics
   curl http://localhost:9090/api/v1/label/__name__/values | jq
   ```

#### Issue 3: Alerts Not Firing

**Symptoms**:
- Conditions met but no alerts
- Alertmanager shows no alerts

**Solutions**:

1. **Check alert rules are loaded**:
   ```bash
   curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | {alert: .name, state: .state}'
   ```

2. **Verify Alertmanager is connected**:
   ```bash
   # Check Alertmanager status
   curl http://localhost:9090/api/v1/alertmanagers | jq
   ```

3. **Test alert rule manually**:
   ```promql
   # Go to Prometheus → Alerts
   # Click on alert to see evaluation
   # Check if query returns results
   ```

4. **Check for silences**:
   ```bash
   curl http://localhost:9093/api/v2/silences | jq
   ```

5. **Restart Prometheus**:
   ```bash
   docker-compose restart prometheus
   ```

#### Issue 4: High Memory Usage

**Symptoms**:
- Prometheus container using excessive memory
- Container getting killed (OOM)

**Solutions**:

1. **Reduce retention time**:
   ```yaml
   # docker-compose.yml
   prometheus:
     command:
       - '--storage.tsdb.retention.time=15d'  # Reduce from 30d
   ```

2. **Reduce scrape frequency**:
   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 30s  # Increase from 15s
   ```

3. **Increase memory limit**:
   ```yaml
   # docker-compose.yml
   prometheus:
     mem_limit: 2g  # Increase from default
   ```

4. **Clean up old data**:
   ```bash
   # Stop Prometheus
   docker-compose stop prometheus
   
   # Delete old data
   docker volume rm autodealgenie_prometheus_data
   
   # Restart
   docker-compose up -d prometheus
   ```

#### Issue 5: Database Exporter Issues

**Symptoms**:
- PostgreSQL/Redis metrics missing
- Exporter targets DOWN in Prometheus

**PostgreSQL Exporter Solutions**:

1. **Check connection string**:
   ```bash
   docker logs autodealgenie-postgres-exporter
   ```

2. **Verify database is accessible**:
   ```bash
   docker exec autodealgenie-postgres-exporter pg_isready -h postgres -U autodealgenie
   ```

3. **Test manual connection**:
   ```bash
   docker exec autodealgenie-postgres psql -U autodealgenie -c "SELECT version();"
   ```

**Redis Exporter Solutions**:

1. **Check Redis connectivity**:
   ```bash
   docker exec autodealgenie-redis-exporter wget -qO- http://localhost:9121/metrics
   ```

2. **Verify Redis is accessible**:
   ```bash
   docker exec autodealgenie-redis redis-cli ping
   ```

### Getting Help

1. **Check logs**:
   ```bash
   # All services
   docker-compose logs --tail=100
   
   # Specific service
   docker logs autodealgenie-prometheus --tail=50
   ```

2. **Verify configuration**:
   ```bash
   # Validate Prometheus config
   docker exec autodealgenie-prometheus promtool check config /etc/prometheus/prometheus.yml
   
   # Validate alert rules
   docker exec autodealgenie-prometheus promtool check rules /etc/prometheus/alerts.yml
   ```

3. **Restart services**:
   ```bash
   # Restart specific service
   docker-compose restart prometheus
   
   # Restart all monitoring
   docker-compose restart prometheus grafana alertmanager
   ```

4. **Check resource usage**:
   ```bash
   docker stats
   ```

5. **Review documentation**:
   - [Prometheus Docs](https://prometheus.io/docs/)
   - [Grafana Docs](https://grafana.com/docs/)
   - [Alertmanager Docs](https://prometheus.io/docs/alerting/latest/alertmanager/)

---

## Best Practices

### Metrics Collection

1. **Use appropriate metric types**:
   - Counter: Monotonically increasing values (requests, errors)
   - Gauge: Values that can go up/down (memory, connections)
   - Histogram: Distributions (latency, request size)
   - Summary: Similar to histogram, cheaper but less flexible

2. **Label wisely**:
   - Keep cardinality low (< 10 values per label)
   - Avoid user-specific or dynamic labels
   - Use consistent label names

3. **Name metrics descriptively**:
   ```
   <namespace>_<subsystem>_<name>_<unit>_<type>
   autodealgenie_deals_created_total
   ```

4. **Include units in metric names**:
   - `_seconds` for time
   - `_bytes` for size
   - `_total` for counters

### Dashboard Design

1. **Group related metrics**: Keep related panels together
2. **Use consistent time ranges**: Default to 1h, provide options
3. **Add panel descriptions**: Document what each panel shows
4. **Use variables**: Make dashboards reusable with template variables
5. **Set appropriate thresholds**: Green/yellow/red for quick identification

### Alerting

1. **Alert on symptoms, not causes**: Alert on user impact
2. **Set appropriate thresholds**: Balance sensitivity vs noise
3. **Include runbook links**: Every alert should have a runbook
4. **Test alerts regularly**: Ensure notifications work
5. **Review and tune**: Adjust thresholds based on experience

### On-Call

1. **Document everything**: Update runbooks after incidents
2. **Communicate clearly**: Keep stakeholders informed
3. **Don't ignore warnings**: Warning alerts prevent critical alerts
4. **Learn from incidents**: Conduct post-mortems
5. **Improve continuously**: Update monitoring based on learnings

---

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [Site Reliability Engineering Book](https://sre.google/books/)
- [Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)

---

## Appendix

### Metric Naming Convention

```
autodealgenie_<component>_<metric>_<unit>_<type>

Examples:
- autodealgenie_deals_created_total (counter)
- autodealgenie_api_latency_seconds (histogram)
- autodealgenie_cache_hit_rate (gauge)
- autodealgenie_db_connections_active (gauge)
```

### Common PromQL Functions

```promql
# Rate of increase
rate(http_requests_total[5m])

# Sum by label
sum by(status) (http_requests_total)

# Percentage
rate(errors[5m]) / rate(requests[5m]) * 100

# Percentile
histogram_quantile(0.95, rate(duration_bucket[5m]))

# Increase over time
increase(counter_total[1h])
```

### Alert Annotation Template

```yaml
annotations:
  summary: "Brief description of the problem"
  description: "Detailed description with context and values"
  runbook: "Link to runbook or troubleshooting steps"
  dashboard: "Link to relevant Grafana dashboard"
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-25  
**Maintained By**: AutoDealGenie Engineering Team

**Docker Compose Configuration:**

```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"  # Jaeger UI
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    environment:
      COLLECTOR_ZIPKIN_HOST_PORT: 9411
```

### OpenTelemetry Integration

```python
# backend/requirements.txt
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-exporter-jaeger==1.21.0

# backend/app/main.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

app = FastAPI(...)
FastAPIInstrumentor.instrument_app(app)
```

### Trace Context Propagation

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@router.get("/deals/{deal_id}")
async def get_deal(deal_id: int):
    with tracer.start_as_current_span("get_deal") as span:
        span.set_attribute("deal.id", deal_id)
        
        # Database call (automatically traced)
        deal = await deal_repository.get(deal_id)
        
        if not deal:
            span.set_attribute("deal.found", False)
            raise HTTPException(404, "Deal not found")
        
        span.set_attribute("deal.found", True)
        span.set_attribute("deal.status", deal.status)
        return deal
```

---

## Health Checks

### Endpoint Implementation

```python
# backend/app/api/v1/endpoints/health.py
from fastapi import APIRouter, status
from sqlalchemy import text

from app.db.session import get_db
from app.db.redis import redis_client
from app.db.mongodb import get_mongodb_client

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependency status"""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {}
    }
    
    # Check PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        health["services"]["postgres"] = "healthy"
    except Exception as e:
        health["services"]["postgres"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check Redis
    try:
        client = redis_client.get_client()
        if client:
            await client.ping()
            health["services"]["redis"] = "healthy"
        else:
            health["services"]["redis"] = "unavailable"
    except Exception as e:
        health["services"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    # Check MongoDB
    try:
        mongo_client = get_mongodb_client()
        await mongo_client.admin.command('ping')
        health["services"]["mongodb"] = "healthy"
    except Exception as e:
        health["services"]["mongodb"] = f"unhealthy: {str(e)}"
        health["status"] = "degraded"
    
    status_code = status.HTTP_200_OK if health["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=health, status_code=status_code)
```

### Kubernetes Liveness and Readiness Probes

```yaml
# k8s/deployment.yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/detailed
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

---

## Alerting

### Alert Rules (Prometheus)

```yaml
# alerts.yml
groups:
  - name: autodealgenie
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} requests/second"

      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High API latency"
          description: "95th percentile latency is {{ $value }}s"

      # Service down
      - alert: ServiceDown
        expr: up{job="autodealgenie-backend"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "AutoDealGenie backend is unreachable"

      # Database connection issues
      - alert: DatabaseConnectionPoolFull
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool nearly full"
          description: "Connection pool is {{ $value }}% utilized"

      # High memory usage
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / node_memory_MemTotal_bytes > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"
```

### Alertmanager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'YOUR_SLACK_WEBHOOK_URL'

route:
  receiver: 'default'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#alerts'
        title: 'AutoDealGenie Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'

  - name: 'slack'
    slack_configs:
      - channel: '#warnings'
        title: 'AutoDealGenie Warning'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## Dashboard Setup

### Grafana Dashboards

**System Overview Dashboard:**
- Request rate
- Error rate
- Response time (p50, p90, p95, p99)
- Active users
- Database connections
- Memory and CPU usage

**Business Metrics Dashboard:**
- Deals created per hour
- User signups
- Authentication success rate
- Top endpoints by usage
- Revenue metrics

**Database Dashboard:**
- Query execution time
- Connection pool utilization
- Slow queries
- Table sizes
- Index hit ratio

### Example Grafana Query

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Database connections
pg_stat_database_numbackends
```

---

## Best Practices

1. **Use structured logging** with consistent field names
2. **Include context** in all logs (request_id, user_id, etc.)
3. **Set appropriate alert thresholds** (not too sensitive, not too lax)
4. **Monitor SLIs/SLOs** (Service Level Indicators/Objectives)
5. **Use distributed tracing** for complex request flows
6. **Implement health checks** for all dependencies
7. **Test alerting** regularly to ensure it works
8. **Create runbooks** for common alerts
9. **Review dashboards** regularly and update as needed
10. **Archive old metrics** to manage storage costs

### SLI/SLO Examples

**Service Level Indicators (SLIs):**
- Availability: % of successful requests
- Latency: % of requests < 500ms
- Throughput: requests per second

**Service Level Objectives (SLOs):**
- 99.9% availability (43 minutes downtime per month)
- 95% of requests complete in < 500ms
- 99% of requests complete in < 2s

---

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Site Reliability Engineering Book](https://sre.google/books/)

---

## Next Steps

1. Set up Prometheus and Grafana
2. Configure alerting rules
3. Implement custom metrics in application
4. Create dashboards for monitoring
5. Test alerting and on-call procedures
6. Document runbooks for common issues
