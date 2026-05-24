# AutoDealGenie

AI-powered automotive deal management platform built with Next.js 14 and Python FastAPI microservices.

## 🚀 Features

- **Next.js 14 Frontend**: Modern React framework with TypeScript, Tailwind CSS, and Server Components
- **FastAPI Backend**: High-performance Python API with async support
- **PostgreSQL + SQLAlchemy**: Robust relational database with ORM and JSONB for flexible data
- **RabbitMQ**: Reliable message broker for event streaming and task queuing
- **Redis**: Fast caching and session management
- **LangChain + OpenAI**: AI-powered insights and automation
- **Prometheus + Grafana**: Comprehensive monitoring and alerting
- **Docker**: Containerized development and deployment
- **Alembic**: Database migration management
- **Black + Ruff**: Code formatting and linting
- **Pre-commit Hooks**: Automated code quality checks
- **Pytest**: Comprehensive testing framework

## 📋 Prerequisites

- Docker and Docker Compose (recommended)
- OR:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 16+
  - RabbitMQ 3.13+
  - Redis 7+

## 🏃 Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/Raviteja77/autodealgenie.git
   cd autodealgenie
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your OpenAI API key
   
   # Frontend
   cp frontend/.env.example frontend/.env.local
   ```

3. **Start all services**
   ```bash
   docker-compose up -d

   stop native Postgres:
   sudo -u postgres /Library/PostgreSQL/18/bin/pg_ctl stop -D /Library/PostgreSQL/18/data
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - API Redoc: http://localhost:8000/redoc

## 🛠️ Manual Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
# With coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🎨 Code Quality

### Backend

```bash
cd backend

# Format code with Black
black .

# Lint with Ruff
ruff check . --fix

# Type checking with MyPy
mypy .

# Install pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Frontend

```bash
cd frontend

# Lint and format
npm run lint
npm run format
```

## 📁 Project Structure

```
autodealgenie/
├── backend/
│   ├── alembic/              # Database migrations
│   │   └── versions/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/  # API endpoints
│   │   │       └── api.py      # Router configuration
│   │   ├── core/               # Configuration
│   │   ├── db/                 # Database connections
│   │   ├── models/             # SQLAlchemy models
│   │   ├── repositories/       # Data access layer
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   └── main.py             # FastAPI application
│   ├── tests/                  # Test suite
│   ├── .env.example
│   ├── .pre-commit-config.yaml
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── app/                    # Next.js 14 app directory
│   │   ├── deals/              # Deals pages
│   │   └── page.tsx            # Home page
│   ├── lib/                    # Utilities
│   │   └── api.ts              # API client
│   ├── .env.example
│   ├── Dockerfile
│   ├── next.config.mjs
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
- `POSTGRES_SERVER`: PostgreSQL host
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name
- `MONGODB_URL`: MongoDB connection string
- `REDIS_HOST`: Redis host
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka servers
- `OPENAI_API_KEY`: OpenAI API key (required for AI features)

#### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/auth/signup` - User signup
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user (requires auth)
- `GET /api/v1/deals/` - List all deals (requires auth)
- `POST /api/v1/deals/` - Create a new deal (requires auth)
- `GET /api/v1/deals/{id}` - Get deal by ID (requires auth)
- `PUT /api/v1/deals/{id}` - Update deal (requires auth)
- `DELETE /api/v1/deals/{id}` - Delete deal (requires auth)

### AI Response Tracking

All AI-generated responses are now comprehensively tracked and stored:
- `GET /api/v1/ai-responses/history/{deal_id}` - Get AI history for a deal
- `GET /api/v1/ai-responses/lifecycle/{deal_id}` - Get complete deal lifecycle
- `GET /api/v1/ai-responses/analytics` - Platform-wide AI analytics (admin)

For detailed documentation on AI response storage, see [AI_STORAGE_ARCHITECTURE.md](AI_STORAGE_ARCHITECTURE.md).

For detailed authentication documentation, see [AUTHENTICATION.md](AUTHENTICATION.md).

## 🐳 Docker Services

The docker-compose setup includes:
- **postgres**: PostgreSQL 16 database
- **mongodb**: MongoDB 7 document database
- **redis**: Redis 7 cache
- **zookeeper**: Kafka coordination service
- **kafka**: Apache Kafka message broker
- **backend**: FastAPI application
- **frontend**: Next.js application
- **prometheus**: Metrics collection and storage
- **grafana**: Visualization and dashboards
- **alertmanager**: Alert routing and notifications
- **postgres-exporter**: PostgreSQL metrics exporter
- **redis-exporter**: Redis metrics exporter

## 📊 Monitoring and Observability

AutoDealGenie includes a comprehensive monitoring stack with Prometheus, Grafana, and Alertmanager.

### Quick Access

- **Prometheus**: http://localhost:9090 - Metrics and alert rules
- **Grafana**: http://localhost:3001 - Dashboards (admin/admin)
- **Alertmanager**: http://localhost:9094 - Alert management
- **Backend Metrics**: http://localhost:8000/metrics - Application metrics

### Pre-configured Dashboards

Three production-ready dashboards are included:

1. **System Overview**: HTTP metrics, latency percentiles, error rates, resource usage
2. **Business Metrics**: Deals created, user signups, authentication stats
3. **Database Performance**: Connection pools, query performance, cache hit rates

### Alert Rules

Pre-configured alerts for:
- **Critical**: Service down, high error rate, database unavailable
- **Warning**: High latency, connection pool exhaustion, low cache hit rate
- **Info**: Unusual traffic patterns, business metrics anomalies

### Configuration

Alert notifications can be configured for:
- **Slack**: Real-time alerts in team channels
- **PagerDuty**: On-call engineer pages for critical issues
- **Email**: Alert summaries and reports

To enable notifications, edit `monitoring/alertmanager/alertmanager.yml` and add your webhook URLs or API keys.

### Testing Monitoring

Run the validation script to verify everything is working:

```bash
./monitoring/test-monitoring.sh
```

### Documentation

For complete monitoring documentation, see:
- [MONITORING.md](MONITORING.md) - Comprehensive monitoring guide with runbooks
- [monitoring/README.md](monitoring/README.md) - Quick reference and setup guide

## 🔄 Database Migrations

### Create a new migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Port Already in Use
If you get port conflicts, change the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Backend
  - "3001:3000"  # Frontend
```

### Database Connection Issues
1. Ensure all containers are running: `docker-compose ps`
2. Check logs: `docker-compose logs backend`
3. Verify environment variables in `.env` files

### OpenAI API Errors
- Make sure you've set a valid `OPENAI_API_KEY` in `backend/.env`
- Check your OpenAI account has sufficient credits

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API docs at `/docs`

## ☁️ Cloud Deployment

### GCP Free Tier Deployment

Deploy AutoDealGenie to Google Cloud Platform Free Tier with minimal costs:

```bash
# Quick deployment
./deploy-gcp.sh dev your-project-id
./deploy-gcp.sh prod your-project-id
```

See [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) for comprehensive deployment guide including:
- Supabase PostgreSQL setup (500MB free)
- Cloud Run deployment (2M requests/month free)
- In-memory caching and queuing for free tier
- Secret Manager configuration
- Monitoring and logging setup
- Cost optimization strategies

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_GUIDE.md](PROJECT_GUIDE.md) | **Start here** — Complete newcomer guide covering architecture, user flows, services, database design, API catalog, and current implementation status |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture blueprint, module dependency maps, data flows, design patterns, coding conventions, and extension points — designed to be given to AI assistants for context |
| [ROADMAP.md](ROADMAP.md) | Strategic development plan with phased features, AI-promptable task descriptions, partner ecosystem strategy, and technical debt tracker |
| [DOCUMENTATION.md](DOCUMENTATION.md) | Detailed technical reference (models, schemas, API examples) |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment checklist |
| [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) | GCP Cloud Run deployment guide |

## 🎯 Roadmap

- [x] User authentication and authorization (JWT-based with HTTP-only cookies)
- [x] GCP Free Tier deployment support
- [x] AI-powered car search with LLM ranking
- [x] Deal management with status tracking
- [x] Lender and insurance recommendations
- [x] Real-time WebSocket negotiation chat
- [x] Monitoring stack (Prometheus + Grafana + Alertmanager)
- [ ] Complete deal evaluation pipeline (Phase 1 — see [ROADMAP.md](ROADMAP.md))
- [ ] Complete AI negotiation agent (Phase 1)
- [ ] Deal summary page (Phase 2)
- [ ] Dynamic partner management (Phase 3)
- [ ] Partner API integration framework (Phase 3)
- [ ] Loan pre-approval flow (Phase 3)
- [ ] Vehicle history integration (Phase 4)
- [ ] Price prediction engine (Phase 4)
- [ ] Mobile application (Phase 5)

> See [ROADMAP.md](ROADMAP.md) for the full strategic plan with AI-promptable task descriptions.