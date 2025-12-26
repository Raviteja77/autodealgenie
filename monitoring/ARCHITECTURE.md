# AutoDealGenie Monitoring Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AutoDealGenie Monitoring Stack                    │
└─────────────────────────────────────────────────────────────────────────┘

                                  Users
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────┐ ┌──────────────┐
            │   Grafana    │ │Prometheus│ │ Alertmanager │
            │  :3001       │ │  :9090   │ │    :9093     │
            │  Dashboards  │ │  Metrics │ │    Alerts    │
            └──────┬───────┘ └────┬─────┘ └──────┬───────┘
                   │              │                │
                   │ Queries      │ Scrapes        │ Notifies
                   │              │                │
                   └──────────────┼────────────────┤
                                  │                │
              ┌───────────────────┴─────┐          │
              │                         │          │
              ▼                         ▼          │
    ┌──────────────────┐      ┌─────────────────┐ │
    │   FastAPI        │      │   Exporters     │ │
    │   Backend        │      │                 │ │
    │   :8000          │      │  Postgres :9187 │ │
    │                  │      │  Redis    :9121 │ │
    │  /metrics        │      │                 │ │
    │  /health         │      │  /metrics       │ │
    └────────┬─────────┘      └────────┬────────┘ │
             │                         │          │
             │ Monitors                │ Monitors │
             │                         │          │
    ┌────────┴─────────────────────────┴────┐     │
    │         Application Services          │     │
    │                                        │     │
    │  ┌──────────┐  ┌──────────┐          │     │
    │  │PostgreSQL│  │ MongoDB  │          │     │
    │  │  :5432   │  │  :27017  │          │     │
    │  └──────────┘  └──────────┘          │     │
    │                                        │     │
    │  ┌──────────┐  ┌──────────┐          │     │
    │  │  Redis   │  │  Kafka   │          │     │
    │  │  :6379   │  │  :9092   │          │     │
    │  └──────────┘  └──────────┘          │     │
    └────────────────────────────────────────┘     │
                                                   │
                                                   │
    ┌──────────────────────────────────────────────┘
    │ Notification Channels
    │
    ├── Slack        (#critical-alerts, #warnings)
    ├── PagerDuty    (On-call engineer pages)
    └── Email        (Alert summaries)
```

## Data Flow

### 1. Metrics Collection
```
FastAPI App ──┬──> Prometheus (HTTP metrics)
              ├──> Business Metrics (deals, users, auth)
              ├──> Database Metrics (queries, connections)
              ├──> Cache Metrics (hit rate, operations)
              └──> LLM Metrics (tokens, requests)

PostgreSQL ───> Postgres Exporter ──> Prometheus
Redis ────────> Redis Exporter ────> Prometheus
```

### 2. Visualization
```
Prometheus ─┬──> Grafana Dashboard 1 (System Overview)
            ├──> Grafana Dashboard 2 (Business Metrics)
            └──> Grafana Dashboard 3 (Database Performance)
```

### 3. Alerting
```
Prometheus ─┬──> Evaluate Alert Rules (every 30s)
            │
            ├──> [Alert: Critical] ──> Alertmanager ──> PagerDuty ──> On-Call
            ├──> [Alert: Warning]  ──> Alertmanager ──> Slack ──> #warnings
            └──> [Alert: Info]     ──> Alertmanager ──> Email ──> Team
```

## Component Responsibilities

### Prometheus (Port 9090)
```
┌─────────────────────────────────────┐
│          Prometheus                 │
├─────────────────────────────────────┤
│ • Scrapes metrics every 15s         │
│ • Stores 30 days of data            │
│ • Evaluates alert rules every 30s   │
│ • Provides PromQL query interface   │
│                                     │
│ Targets:                            │
│  ✓ autodealgenie-backend:8000       │
│  ✓ postgres-exporter:9187           │
│  ✓ redis-exporter:9121              │
│  ✓ prometheus:9090 (self)           │
│  ✓ alertmanager:9093                │
└─────────────────────────────────────┘
```

### Grafana (Port 3001)
```
┌─────────────────────────────────────┐
│            Grafana                  │
├─────────────────────────────────────┤
│ • Visualizes Prometheus data        │
│ • 3 pre-configured dashboards       │
│ • 22 panels across all dashboards   │
│ • Auto-loads datasource             │
│ • Refresh: 10s-30s                  │
│                                     │
│ Dashboards:                         │
│  ✓ System Overview (7 panels)       │
│  ✓ Business Metrics (7 panels)      │
│  ✓ Database Performance (8 panels)  │
└─────────────────────────────────────┘
```

### Alertmanager (Port 9093)
```
┌─────────────────────────────────────┐
│         Alertmanager                │
├─────────────────────────────────────┤
│ • Receives alerts from Prometheus   │
│ • Groups related alerts             │
│ • Routes by severity & component    │
│ • Manages notification channels     │
│                                     │
│ Routing:                            │
│  Critical → PagerDuty (immediate)   │
│  Warning  → Slack (1h)              │
│  Info     → Email (daily)           │
│                                     │
│ Features:                           │
│  • Alert silencing                  │
│  • Inhibition rules                 │
│  • Notification templates           │
└─────────────────────────────────────┘
```

### FastAPI Backend (Port 8000)
```
┌─────────────────────────────────────┐
│       FastAPI Application           │
├─────────────────────────────────────┤
│ • Exposes /metrics endpoint         │
│ • Auto-instrumented HTTP metrics    │
│ • Custom business metrics           │
│                                     │
│ Metrics Exported:                   │
│  ✓ http_requests_total              │
│  ✓ http_request_duration_seconds    │
│  ✓ autodealgenie_deals_created      │
│  ✓ autodealgenie_user_signups       │
│  ✓ autodealgenie_auth_success/fail  │
│  ✓ Database query metrics           │
│  ✓ Cache operation metrics          │
│  ✓ LLM request metrics              │
└─────────────────────────────────────┘
```

## Metrics Categories

### HTTP Metrics (Auto-instrumented)
```
┌─────────────────────────────────────┐
│ HTTP Metrics                        │
├─────────────────────────────────────┤
│ • Requests: Total, Rate, By status  │
│ • Latency: p50, p90, p95, p99       │
│ • Size: Request & Response bytes    │
│ • In-flight: Current requests       │
└─────────────────────────────────────┘
```

### Business Metrics
```
┌─────────────────────────────────────┐
│ Business Metrics                    │
├─────────────────────────────────────┤
│ • Deals: Created, By status         │
│ • Users: Signups, Active            │
│ • Auth: Success/Failure rate        │
│ • Searches: Count, Duration         │
│ • Negotiations: Sessions, Messages  │
│ • Loans: Applications, Status       │
└─────────────────────────────────────┘
```

### Database Metrics
```
┌─────────────────────────────────────┐
│ Database Metrics                    │
├─────────────────────────────────────┤
│ PostgreSQL:                         │
│ • Connections: Active, Max, %       │
│ • Transactions: Commits, Rollbacks  │
│ • Operations: Insert, Update, Delete│
│                                     │
│ Redis:                              │
│ • Memory: Used, Max, %              │
│ • Hit Rate: Hits/(Hits+Misses)      │
│ • Commands: Rate, Total             │
│ • Clients: Connected                │
└─────────────────────────────────────┘
```

## Alert Flow

### Critical Alert Example
```
Condition Met
    │
    ▼
[High Error Rate > 5% for 5 min]
    │
    ▼
Prometheus fires alert
    │
    ▼
Alertmanager receives
    │
    ├─> Group by: alertname, severity
    ├─> Wait: 10s for more alerts
    │
    ▼
Route by severity: Critical
    │
    ▼
Send to: PagerDuty
    │
    ▼
On-call engineer paged
    │
    ├─> Acknowledge (5 min)
    ├─> Investigate (using runbook)
    ├─> Mitigate/Resolve
    └─> Document in post-mortem
```

## Monitoring Workflow

### Development
```
1. Developer commits code
2. CI/CD runs tests
3. Deploy to dev environment
4. Monitoring starts automatically
5. Check Grafana dashboards
6. Verify metrics are collected
7. Test alerts (if applicable)
```

### Production
```
1. Deploy to production
2. Monitor dashboards in real-time
3. Alerts fire if issues detected
4. On-call responds to critical alerts
5. Team investigates using runbooks
6. Issue resolved and documented
7. Alert thresholds tuned if needed
```

## Scaling Considerations

### Current Setup (Development)
```
┌────────────────────────────────────┐
│ Single Server                      │
│ • All services on one host         │
│ • 30-day retention                 │
│ • 15s scrape interval              │
│ • Good for: Dev, Small deployments │
└────────────────────────────────────┘
```

### Production Scaling
```
┌────────────────────────────────────┐
│ Distributed Setup                  │
│ • Multiple Prometheus instances    │
│ • Thanos/Cortex for long-term      │
│ • Grafana HA with load balancer    │
│ • Remote write to cloud storage    │
│ • Alertmanager cluster             │
└────────────────────────────────────┘
```

## Integration Points

### External Services
```
Prometheus ─┬─> Thanos (Long-term storage)
            ├─> Cortex (Multi-tenant metrics)
            └─> VictoriaMetrics (Time series DB)

Grafana ────┬─> LDAP/OAuth (Authentication)
            ├─> Cloud storage (Dashboard backup)
            └─> API (Programmatic access)

Alertmanager─┬─> Slack (Team notifications)
            ├─> PagerDuty (On-call pages)
            ├─> Email (Reports & summaries)
            ├─> Webhook (Custom integrations)
            └─> OpsGenie (Incident management)
```

## Ports Summary

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Backend | 8000 | HTTP | API + /metrics |
| Prometheus | 9090 | HTTP | Metrics & UI |
| Grafana | 3001 | HTTP | Dashboards |
| Alertmanager | 9093 | HTTP | Alerts & UI |
| PostgreSQL Exporter | 9187 | HTTP | DB metrics |
| Redis Exporter | 9121 | HTTP | Cache metrics |

## Storage Volumes

```
prometheus_data/     # Prometheus time series database
├── chunks/          # Metric data chunks
├── wal/             # Write-ahead log
└── queries.active   # Active queries

grafana_data/        # Grafana configuration
├── grafana.db       # SQLite database
├── plugins/         # Grafana plugins
└── sessions/        # User sessions

alertmanager_data/   # Alertmanager state
├── nflog            # Notification log
└── silences         # Active silences
```

---

**Version**: 1.0  
**Last Updated**: 2025-12-25  
**Architecture**: Production-ready, horizontally scalable
