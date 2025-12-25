# Monitoring and Observability Guide

Comprehensive guide for monitoring AutoDealGenie application in production.

## Table of Contents

1. [Overview](#overview)
2. [Logging](#logging)
3. [Metrics](#metrics)
4. [Distributed Tracing](#distributed-tracing)
5. [Health Checks](#health-checks)
6. [Alerting](#alerting)
7. [Dashboard Setup](#dashboard-setup)
8. [Best Practices](#best-practices)

---

## Overview

AutoDealGenie uses a multi-layered observability approach:

- **Logs**: Structured JSON logs for debugging and audit trails
- **Metrics**: Performance and business metrics tracking
- **Traces**: Distributed request tracing across services
- **Health Checks**: Service health and dependency status

### Recommended Stack

- **Logs**: Loki or ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Prometheus + Grafana
- **Tracing**: Jaeger or Zipkin
- **APM**: Sentry for error tracking

---

## Logging

### Log Configuration

Logs are configured in `backend/app/core/logging.py`:

**Development**: Human-readable console logs
```
2025-12-25 16:30:00 - app.api.endpoints - INFO - [auth.py:52] - User logged in successfully
```

**Production**: JSON-structured logs
```json
{
  "timestamp": "2025-12-25T16:30:00.000Z",
  "level": "INFO",
  "message": "User logged in successfully",
  "module": "auth",
  "function": "login",
  "line": 52,
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123
}
```

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical failures requiring immediate attention

### Log Aggregation with Loki

**Docker Compose Configuration:**

```yaml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    volumes:
      - loki_data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  loki_data:
  grafana_data:
```

**Promtail Configuration (promtail-config.yml):**

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: autodealgenie-backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: autodealgenie-backend
          __path__: /var/log/autodealgenie/*.log
```

### Logging Best Practices

1. **Always include request_id** for request correlation
2. **Use structured logging** with JSON in production
3. **Log at appropriate levels** (don't log everything as INFO)
4. **Include context** (user_id, deal_id, etc.)
5. **Sanitize sensitive data** (passwords, tokens, PII)

**Example:**

```python
import logging

logger = logging.getLogger(__name__)

# Good logging
logger.info(
    "Deal created successfully",
    extra={
        "user_id": user.id,
        "deal_id": deal.id,
        "vehicle_make": deal.vehicle_make,
        "request_id": request.state.request_id
    }
)

# Bad logging - missing context
logger.info("Deal created")
```

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

### Key Metrics to Track

**Application Metrics:**
- Request rate (requests per second)
- Response time (latency percentiles: p50, p90, p95, p99)
- Error rate (4xx, 5xx responses)
- Request size and response size

**Business Metrics:**
- Deals created per hour
- User signups per day
- Authentication success/failure rate
- API endpoint usage distribution

**System Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

**Database Metrics:**
- Connection pool utilization
- Query execution time
- Slow queries (> 1s)
- Active connections

**Redis Metrics:**
- Cache hit ratio
- Memory usage
- Key count
- Commands per second

### Custom Metrics Example

```python
from prometheus_client import Counter, Histogram

# Define metrics
deals_created = Counter(
    'autodealgenie_deals_created_total',
    'Total number of deals created',
    ['status']
)

deal_processing_time = Histogram(
    'autodealgenie_deal_processing_seconds',
    'Time spent processing deals',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Use metrics
@router.post("/deals/")
async def create_deal(deal: DealCreate):
    with deal_processing_time.time():
        # Create deal
        new_deal = await deal_service.create(deal)
        deals_created.labels(status=new_deal.status).inc()
        return new_deal
```

---

## Distributed Tracing

### Jaeger Setup

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
