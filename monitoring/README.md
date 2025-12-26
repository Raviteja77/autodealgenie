# AutoDealGenie Monitoring Stack

Complete monitoring solution for AutoDealGenie using Prometheus, Grafana, and Alertmanager.

## Quick Start

```bash
# Start monitoring stack with the application
docker-compose up -d

# Access services
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)
# - Alertmanager: http://localhost:9094
# - Backend Metrics: http://localhost:8000/metrics
```

## Directory Structure

```
monitoring/
├── prometheus/
│   ├── prometheus.yml      # Prometheus configuration
│   └── alerts.yml          # Alert rules
├── alertmanager/
│   └── alertmanager.yml    # Alertmanager configuration
└── grafana/
    ├── provisioning/
    │   ├── datasources/    # Auto-configure Prometheus datasource
    │   └── dashboards/     # Auto-load dashboards
    └── dashboards/
        ├── system-overview.json          # System health dashboard
        ├── business-metrics.json         # Business KPIs dashboard
        └── database-performance.json     # Database metrics dashboard
```

## Components

### Prometheus (Port 9090)

Metrics collection and storage system.

**Key Features**:
- Scrapes metrics every 15 seconds
- Stores 30 days of data
- Evaluates alert rules every 30 seconds

**Configuration**: `prometheus/prometheus.yml`

**Targets**:
- `autodealgenie-backend:8000` - FastAPI application metrics
- `postgres-exporter:9187` - PostgreSQL metrics
- `redis-exporter:9121` - Redis metrics

### Grafana (Port 3001)

Visualization and dashboards.

**Default Credentials**:
- Username: `admin`
- Password: `admin`

**Pre-configured Dashboards**:
1. **System Overview**: Application health and performance
2. **Business Metrics**: Deals, users, authentication
3. **Database Performance**: PostgreSQL and Redis metrics

**Configuration**: `grafana/provisioning/`

### Alertmanager (Port 9094)

Alert routing and notification management.

**Features**:
- Groups related alerts
- Routes by severity and component
- Supports Slack, PagerDuty, email notifications

**Configuration**: `alertmanager/alertmanager.yml`

### Exporters

**PostgreSQL Exporter** (Port 9187):
- Exports database metrics
- Connection pool statistics
- Query performance

**Redis Exporter** (Port 9121):
- Cache metrics
- Memory usage
- Hit/miss rates

## Available Metrics

### HTTP Metrics (Auto-instrumented)
- `http_requests_total` - Total requests by method, status
- `http_request_duration_seconds` - Request latency (histogram)
- `http_request_size_bytes` - Request body size
- `http_response_size_bytes` - Response body size

### Business Metrics
- `autodealgenie_deals_created_total{status}` - Deals created by status
- `autodealgenie_user_signups_total` - User registrations
- `autodealgenie_auth_success_total` - Successful logins
- `autodealgenie_auth_failures_total` - Failed login attempts

### Database Metrics
- `pg_stat_database_numbackends` - Active connections
- `pg_stat_database_xact_commit` - Committed transactions
- `redis_memory_used_bytes` - Redis memory usage
- `redis_keyspace_hits_total` - Cache hits

See [MONITORING.md](../MONITORING.md) for complete metrics list.

## Alert Rules

### Critical Alerts
- **ServiceDown**: Backend unreachable for 2 minutes
- **HighErrorRate**: > 5% error rate for 5 minutes
- **DatabaseDown**: PostgreSQL unreachable
- **RedisDown**: Redis cache unavailable

### Warning Alerts
- **HighAPILatency**: p95 latency > 2s for 10 minutes
- **DatabaseConnectionPoolHigh**: > 80% utilization
- **LowCacheHitRate**: < 80% hit rate
- **HighRedisMemoryUsage**: > 90% memory used

See `prometheus/alerts.yml` for complete list.

## Configuration

### Enabling Slack Notifications

1. Create Slack webhook at https://api.slack.com/apps
2. Edit `alertmanager/alertmanager.yml`:
   ```yaml
   global:
     slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
   ```
3. Uncomment Slack receiver configurations
4. Restart Alertmanager:
   ```bash
   docker-compose restart alertmanager
   ```

### Enabling PagerDuty Integration

1. Get PagerDuty integration key from your service
2. Edit `alertmanager/alertmanager.yml`:
   ```yaml
   receivers:
     - name: 'critical-alerts'
       pagerduty_configs:
         - service_key: 'YOUR_PAGERDUTY_KEY'
   ```
3. Restart Alertmanager

### Customizing Alert Thresholds

Edit `prometheus/alerts.yml`:

```yaml
# Example: Change high error rate threshold
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.10  # Changed from 0.05
  for: 5m
```

Reload Prometheus:
```bash
curl -X POST http://localhost:9090/-/reload
```

## Testing

### Verify Setup

```bash
# Check all services are healthy
docker-compose ps

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Test metrics endpoint
curl http://localhost:8000/metrics | grep http_requests_total
```

### Generate Test Traffic

```bash
# Generate requests
for i in {1..100}; do
  curl http://localhost:8000/health
done

# Wait 15 seconds for Prometheus to scrape
sleep 15

# Check metric increased
curl http://localhost:8000/metrics | grep http_requests_total
```

### Test Alert

```bash
# Trigger 404 errors (high error rate)
for i in {1..100}; do
  curl http://localhost:8000/nonexistent
done

# Wait 5 minutes and check alerts
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {alert: .labels.alertname, state: .state}'
```

## Accessing Dashboards

1. Open Grafana: http://localhost:3001
2. Login with `admin/admin`
3. Navigate to Dashboards → Browse
4. Select from "AutoDealGenie" folder:
   - System Overview
   - Business Metrics
   - Database Performance

## Troubleshooting

### Prometheus Shows Targets Down

```bash
# Check backend is accessible
curl http://localhost:8000/health

# Check from Prometheus container
docker exec autodealgenie-prometheus wget -qO- http://backend:8000/metrics

# View Prometheus logs
docker logs autodealgenie-prometheus --tail 50
```

### Grafana Shows "No Data"

```bash
# Test Prometheus datasource
# Grafana → Configuration → Data Sources → Prometheus → Test

# Query Prometheus directly
curl 'http://localhost:9090/api/v1/query?query=up' | jq

# Check time range in dashboard (top right)
```

### Alerts Not Firing

```bash
# Verify alert rules are loaded
curl http://localhost:9090/api/v1/rules | jq

# Check Alertmanager connection
curl http://localhost:9090/api/v1/alertmanagers | jq

# View Alertmanager logs
docker logs autodealgenie-alertmanager --tail 50
```

## Maintenance

### Backup Grafana Dashboards

```bash
# Export dashboard JSON
# Grafana → Dashboard → Settings → JSON Model → Copy

# Save to dashboards directory
cat > monitoring/grafana/dashboards/my-dashboard.json
```

### Clean Up Old Prometheus Data

```bash
# Stop Prometheus
docker-compose stop prometheus

# Remove old data
docker volume rm autodealgenie_prometheus_data

# Restart
docker-compose up -d prometheus
```

### Update Alert Rules

1. Edit `prometheus/alerts.yml`
2. Reload Prometheus:
   ```bash
   curl -X POST http://localhost:9090/-/reload
   ```
3. Verify rules loaded:
   ```bash
   curl http://localhost:9090/api/v1/rules | jq
   ```

## Production Deployment

### Recommended Changes

1. **Change Grafana password**:
   ```yaml
   # docker-compose.yml
   grafana:
     environment:
       - GF_SECURITY_ADMIN_PASSWORD=<strong-password>
   ```

2. **Configure persistent storage**:
   - Ensure volumes are backed up
   - Use cloud storage for Prometheus data

3. **Enable HTTPS**:
   - Configure reverse proxy (nginx)
   - Use Let's Encrypt certificates

4. **Set up external storage**:
   - Use remote write for long-term storage
   - Consider Thanos or Cortex for scalability

5. **Configure authentication**:
   - Enable OAuth for Grafana
   - Restrict Prometheus/Alertmanager access

### Security Best Practices

- Change default passwords
- Use HTTPS for all connections
- Implement network policies
- Regular security updates
- Audit access logs

## Resources

- [Complete Documentation](../MONITORING.md)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alert Runbooks](../MONITORING.md#runbooks)
- [On-Call Procedures](../MONITORING.md#on-call-procedures)

## Support

For issues or questions:
1. Check [Troubleshooting Guide](../MONITORING.md#troubleshooting)
2. Review [Runbooks](../MONITORING.md#runbooks)
3. Contact DevOps team

---

**Version**: 1.0  
**Last Updated**: 2025-12-25
