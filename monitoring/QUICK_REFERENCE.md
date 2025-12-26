# AutoDealGenie Monitoring Stack - Quick Reference Card

## 🔗 Service URLs

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Prometheus** | http://localhost:9090 | None | Metrics & Alert Rules |
| **Grafana** | http://localhost:3001 | admin/admin | Dashboards & Visualization |
| **Alertmanager** | http://localhost:9093 | None | Alert Management |
| **Backend Metrics** | http://localhost:8000/metrics | None | Raw Prometheus Metrics |
| **Backend API Docs** | http://localhost:8000/docs | None | API Documentation |
| **PostgreSQL Exporter** | http://localhost:9187/metrics | None | Database Metrics |
| **Redis Exporter** | http://localhost:9121/metrics | None | Cache Metrics |

## 📊 Pre-configured Dashboards

### 1. System Overview
**Purpose**: Real-time application health  
**URL**: Grafana → Dashboards → System Overview  
**Panels**:
- Request Rate
- Error Rate  
- API Latency (p50, p90, p95, p99)
- HTTP Status Codes
- Database Connections
- Redis Memory
- App Memory

### 2. Business Metrics
**Purpose**: Business KPIs  
**URL**: Grafana → Dashboards → Business Metrics  
**Panels**:
- Deals Created/Hour
- User Signups/Hour
- Auth Success Rate
- Total Deals (24h)
- Top Endpoints
- Auth Failures
- Deals by Status

### 3. Database Performance
**Purpose**: Database health  
**URL**: Grafana → Dashboards → Database Performance  
**Panels**:
- Connection Pool
- Transactions
- Operations (Insert/Update/Delete)
- Redis Memory
- Cache Hit Rate
- Redis Commands
- Connected Clients

## 🚨 Alert Summary

### Critical Alerts (Response: 5 min)
- 🔴 **ServiceDown** - Backend unreachable (2 min)
- 🔴 **HighErrorRate** - >5% errors (5 min)
- 🔴 **DatabaseDown** - PostgreSQL unavailable (2 min)
- 🔴 **RedisDown** - Redis unavailable (2 min)
- 🔴 **DiskSpaceLow** - <10% disk space (5 min)

### Warning Alerts (Response: 30 min)
- 🟡 **HighAPILatency** - p95 >2s (10 min)
- 🟡 **HighRequestRate** - >100 req/s (10 min)
- 🟡 **DatabaseConnectionPoolHigh** - >80% (5 min)
- 🟡 **LowCacheHitRate** - <80% (15 min)
- 🟡 **HighRedisMemoryUsage** - >90% (5 min)
- 🟡 **SlowQueries** - avg >1s (10 min)

### Info Alerts (Response: Next day)
- 🔵 **LowUserSignupRate** - <0.01/hour (2 hours)
- 🔵 **HighAuthenticationFailureRate** - >5/s (10 min)

## 📈 Key Metrics

### HTTP Metrics
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Business Metrics
```promql
# Deals created in last hour
increase(autodealgenie_deals_created_total[1h])

# User signups today
increase(autodealgenie_user_signups_total[24h])

# Auth success rate
rate(autodealgenie_auth_success_total[5m]) / 
  (rate(autodealgenie_auth_success_total[5m]) + 
   rate(autodealgenie_auth_failures_total[5m]))
```

### Database Metrics
```promql
# Connection pool utilization
pg_stat_database_numbackends / pg_settings_max_connections

# Cache hit rate
rate(redis_keyspace_hits_total[5m]) / 
  (rate(redis_keyspace_hits_total[5m]) + 
   rate(redis_keyspace_misses_total[5m]))

# Transactions per second
rate(pg_stat_database_xact_commit[5m])
```

## 🛠️ Common Commands

### Start Monitoring
```bash
docker-compose up -d
```

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs --tail=50

# Specific service
docker logs autodealgenie-prometheus --tail=50
docker logs autodealgenie-grafana --tail=50
```

### Test Monitoring Stack
```bash
./monitoring/test-monitoring.sh
```

### Restart Services
```bash
# Restart all monitoring
docker-compose restart prometheus grafana alertmanager

# Restart specific service
docker-compose restart prometheus
```

### Reload Prometheus Config
```bash
curl -X POST http://localhost:9090/-/reload
```

## 🔧 Quick Troubleshooting

### Prometheus Targets Down
```bash
# Check backend is running
curl http://localhost:8000/health

# Check from Prometheus container
docker exec autodealgenie-prometheus wget -qO- http://backend:8000/metrics

# View logs
docker logs autodealgenie-prometheus
```

### Grafana Shows "No Data"
```bash
# Test datasource
curl 'http://localhost:9090/api/v1/query?query=up'

# Check Grafana datasource
# Grafana → Configuration → Data Sources → Prometheus → Test
```

### Alerts Not Firing
```bash
# Check alert rules loaded
curl http://localhost:9090/api/v1/rules | jq

# Check Alertmanager connection
curl http://localhost:9090/api/v1/alertmanagers | jq

# View current alerts
curl http://localhost:9090/api/v1/alerts | jq
```

## 📚 Documentation

### Primary Docs
- **MONITORING.md** - Complete 500+ line guide
  - Setup instructions
  - Architecture
  - Metrics reference
  - Alert rules
  - Runbooks
  - On-call procedures
  - Testing & troubleshooting

### Quick Reference
- **monitoring/README.md** - Quick start guide
- **monitoring/IMPLEMENTATION_SUMMARY.md** - Implementation details
- **README.md** - Project overview

## 🔔 Notification Setup

### Slack
Edit `monitoring/alertmanager/alertmanager.yml`:
```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK'

receivers:
  - name: 'critical-alerts'
    slack_configs:
      - channel: '#critical-alerts'
```

### PagerDuty
```yaml
receivers:
  - name: 'critical-alerts'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

### Email
```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@autodealgenie.com'
  smtp_auth_username: 'alerts@autodealgenie.com'
  smtp_auth_password: 'your-password'
```

After configuration:
```bash
docker-compose restart alertmanager
```

## 🎯 First Steps After Setup

1. ✅ Start all services: `docker-compose up -d`
2. ✅ Check services are healthy: `docker-compose ps`
3. ✅ Run validation: `./monitoring/test-monitoring.sh`
4. ✅ Access Grafana: http://localhost:3001 (admin/admin)
5. ✅ View dashboards in "AutoDealGenie" folder
6. ✅ Check Prometheus targets: http://localhost:9090/targets
7. ✅ Generate test traffic and verify metrics
8. ⚠️ Configure alert notifications (Slack/PagerDuty)
9. ⚠️ Change Grafana admin password for production

## 📞 Support

**Issues?** Check the troubleshooting section in MONITORING.md

**Questions?** Review the comprehensive documentation:
- MONITORING.md - Complete guide
- monitoring/README.md - Quick reference
- Docker logs - `docker-compose logs <service>`

---

**Version**: 1.0  
**Last Updated**: 2025-12-25  
**Status**: Production Ready (requires notification config)
