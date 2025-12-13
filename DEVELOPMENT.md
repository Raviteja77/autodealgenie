# Development Guide

## Architecture Overview

AutoDealGenie follows a microservices architecture with clear separation of concerns:

### Backend Architecture

```
backend/
├── app/
│   ├── api/v1/         # API routes and endpoints
│   ├── core/           # Configuration and settings
│   ├── db/             # Database connections (PostgreSQL, MongoDB, Redis)
│   ├── models/         # SQLAlchemy ORM models
│   ├── repositories/   # Data access layer
│   ├── schemas/        # Pydantic models for validation
│   └── services/       # Business logic (Kafka, LangChain)
```

**Layer Responsibilities:**

1. **API Layer** (`api/v1/endpoints/`): HTTP request/response handling
2. **Schema Layer** (`schemas/`): Data validation with Pydantic
3. **Service Layer** (`services/`): Business logic and external integrations
4. **Repository Layer** (`repositories/`): Database operations
5. **Model Layer** (`models/`): Database table definitions

### Frontend Architecture

```
frontend/
├── app/
│   ├── (routes)/       # Next.js 14 app router pages
│   └── layout.tsx      # Root layout
└── lib/
    └── api.ts          # API client
```

## Development Workflow

### 1. Setting Up Development Environment

**Option A: Docker (Recommended)**
```bash
./start.sh
```

**Option B: Manual Setup**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### 2. Database Migrations

**Create a new migration:**
```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```

### 3. Adding New Features

#### Adding a New API Endpoint

1. **Define the model** in `backend/app/models/models.py`
```python
class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True)
    make = Column(String(100))
    model = Column(String(100))
```

2. **Define schemas** in `backend/app/schemas/schemas.py`
```python
class VehicleBase(BaseModel):
    make: str
    model: str

class VehicleResponse(VehicleBase):
    id: int
    class Config:
        from_attributes = True
```

3. **Create repository** in `backend/app/repositories/`
```python
class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, vehicle_in: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**vehicle_in.model_dump())
        self.db.add(vehicle)
        self.db.commit()
        return vehicle
```

4. **Add endpoint** in `backend/app/api/v1/endpoints/`
```python
@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    repository = VehicleRepository(db)
    return repository.create(vehicle)
```

5. **Register router** in `backend/app/api/v1/api.py`
```python
from app.api.v1.endpoints import vehicles
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
```

#### Adding a Frontend Page

1. **Create page** in `frontend/app/[route]/page.tsx`
```tsx
export default function MyPage() {
  return <div>My Page</div>;
}
```

2. **Use API client** in `frontend/lib/api.ts`
```typescript
async getVehicles(): Promise<Vehicle[]> {
  return this.request<Vehicle[]>('/vehicles/');
}
```

### 4. Testing

#### Backend Tests
```bash
cd backend
pytest                           # Run all tests
pytest tests/test_deals.py       # Run specific test
pytest --cov=app                 # With coverage
```

#### Writing Tests
```python
def test_create_deal(client):
    deal_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": 2022,
        "asking_price": 25000.00,
    }
    response = client.post("/api/v1/deals/", json=deal_data)
    assert response.status_code == 201
```

### 5. Code Quality

#### Format Code
```bash
cd backend
black .                          # Format Python code
ruff check . --fix               # Lint and fix
```

#### Pre-commit Hooks
```bash
cd backend
pre-commit install               # Install hooks
pre-commit run --all-files       # Run manually
```

### 6. Working with Services

#### Kafka Producer
```python
from app.services.kafka_producer import kafka_producer

await kafka_producer.send_deal_event({
    "deal_id": 123,
    "status": "created"
})
```

#### Kafka Consumer
```python
from app.services.kafka_consumer import deals_consumer, handle_deal_message

# Start consumer
await deals_consumer.start()
await deals_consumer.consume_messages(handle_deal_message)
```

#### LangChain Service
```python
from app.services.langchain_service import langchain_service

analysis = await langchain_service.analyze_vehicle_price(
    make="Toyota",
    model="Camry",
    year=2022,
    mileage=15000,
    condition="excellent",
    asking_price=25000.0
)
```

## Environment Variables

### Required
- `OPENAI_API_KEY`: For AI features

### Database
- `POSTGRES_*`: PostgreSQL connection
- `MONGODB_URL`: MongoDB connection
- `REDIS_HOST`: Redis connection

### Optional
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka connection
- `SECRET_KEY`: JWT secret

## Common Issues

### Issue: Port already in use
**Solution:** Change ports in docker-compose.yml or stop conflicting services

### Issue: Database connection error
**Solution:** Ensure PostgreSQL is running and credentials are correct

### Issue: OpenAI API errors
**Solution:** Check API key and account credits

## Best Practices

1. **Always create feature branches**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write tests for new features**
   - Unit tests for business logic
   - Integration tests for API endpoints

3. **Use type hints in Python**
   ```python
   def get_deal(deal_id: int) -> Optional[Deal]:
       pass
   ```

4. **Use TypeScript in frontend**
   ```typescript
   interface Deal {
       id: number;
       customer_name: string;
   }
   ```

5. **Document complex logic**
   - Add docstrings to functions
   - Comment non-obvious code

6. **Follow naming conventions**
   - Python: snake_case
   - TypeScript: camelCase
   - Classes: PascalCase

## Debugging

### Backend
```bash
# View logs
docker compose logs -f backend

# Access container
docker compose exec backend bash

# Python debugger
import pdb; pdb.set_trace()
```

### Frontend
```bash
# View logs
docker compose logs -f frontend

# Browser DevTools
# Use React DevTools extension
```

## Performance Tips

1. **Use database indexes** for frequently queried fields
2. **Cache with Redis** for expensive operations
3. **Use async/await** for I/O operations
4. **Optimize database queries** (avoid N+1 queries)
5. **Use Kafka** for async processing

## Security Considerations

1. **Never commit secrets** to version control
2. **Use environment variables** for sensitive data
3. **Validate all inputs** with Pydantic
4. **Use HTTPS** in production
5. **Implement rate limiting** for APIs
6. **Keep dependencies updated**

## Deployment

See README.md for production deployment instructions.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [LangChain Documentation](https://python.langchain.com/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
