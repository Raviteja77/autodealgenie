# Testing Guide

Comprehensive guide for testing AutoDealGenie application.

## Table of Contents

1. [Overview](#overview)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Integration Testing](#integration-testing)
5. [E2E Testing](#e2e-testing)
6. [Test Coverage](#test-coverage)
7. [Best Practices](#best-practices)

---

## Overview

AutoDealGenie uses a comprehensive testing strategy:

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints with database
- **E2E Tests**: Test complete user workflows
- **Coverage Goals**: Minimum 80% for critical modules

### Test Stack

**Backend:**
- pytest: Testing framework
- pytest-asyncio: Async test support
- pytest-cov: Coverage reporting
- httpx: HTTP client for testing

**Frontend:**
- Jest: Testing framework
- Testing Library: React component testing
- Playwright: E2E testing (planned)

---

## Backend Testing

### Setup Test Environment

1. **Create test environment file:**
```bash
cd backend
cp .env.test.example .env.test
```

2. **Configure test database:**
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=test_user
POSTGRES_PASSWORD=test_password
POSTGRES_DB=autodealgenie_test
SECRET_KEY=test-secret-key-min-32-chars-for-testing
ENVIRONMENT=testing
```

3. **Start test services:**
```bash
docker-compose up -d postgres redis
```

### Running Tests

**Run all tests:**
```bash
cd backend
pytest
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

**Run specific test file:**
```bash
pytest tests/test_auth.py
```

**Run specific test:**
```bash
pytest tests/test_auth.py::test_signup_success -v
```

**Run with output:**
```bash
pytest -v -s
```

**Run only failed tests:**
```bash
pytest --lf
```

### Test Structure

```
backend/tests/
├── conftest.py              # Fixtures and configuration
├── test_auth.py            # Authentication tests
├── test_deals.py           # Deal management tests
├── test_repositories.py    # Repository layer tests
├── test_services.py        # Service layer tests
├── test_security.py        # Security tests
├── test_rate_limiter.py    # Rate limiting tests
└── llm/                    # LLM integration tests
    ├── test_llm_client.py
    ├── test_prompts.py
    └── test_schemas.py
```

### Writing Tests

**Example: Testing an endpoint**

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_deal(async_client: AsyncClient, auth_headers: dict):
    """Test creating a new deal"""
    response = await async_client.post(
        "/api/v1/deals/",
        json={
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "vehicle_make": "Toyota",
            "vehicle_model": "Camry",
            "vehicle_year": 2022,
            "vehicle_mileage": 15000,
            "vehicle_vin": "1HGBH41JXMN109186",
            "asking_price": 28000.00
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "John Doe"
    assert data["status"] == "pending"
```

**Example: Testing a service**

```python
import pytest
from app.services.deal_service import DealService
from app.schemas.deal import DealCreate

@pytest.mark.asyncio
async def test_deal_service_create(db_session):
    """Test deal service creation"""
    service = DealService(db_session)
    deal_data = DealCreate(
        customer_name="Jane Smith",
        customer_email="jane@example.com",
        vehicle_make="Honda",
        vehicle_model="Accord",
        vehicle_year=2023,
        vehicle_mileage=5000,
        vehicle_vin="1HGCY1F30LA000001",
        asking_price=32000.00
    )
    
    deal = await service.create_deal(deal_data)
    assert deal.id is not None
    assert deal.customer_name == "Jane Smith"
```

### Common Fixtures

Located in `conftest.py`:

```python
@pytest.fixture
async def async_client():
    """Async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def db_session():
    """Database session for testing"""
    # Setup: create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Teardown: drop tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Authentication headers with valid token"""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

### Coverage Exclusions

Configured in `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "app/db/mongodb.py",
    "app/db/redis.py",
    "app/services/kafka_consumer.py",
    "app/services/kafka_producer.py",
    "app/services/langchain_service.py",
    "app/services/car_recommendation_service.py",
    "app/tools/marketcheck_client.py",
]
```

---

## Frontend Testing

### Running Tests

**Run all tests:**
```bash
cd frontend
npm test
```

**Run with coverage:**
```bash
npm test -- --coverage
```

**Run in watch mode:**
```bash
npm test -- --watch
```

**Update snapshots:**
```bash
npm test -- -u
```

### Test Structure

```
frontend/__tests__/
├── components/
│   ├── ErrorBoundary.test.tsx
│   ├── VehicleCard.test.tsx
│   └── ...
├── lib/
│   ├── api.test.ts
│   ├── errors.test.ts
│   └── ...
└── pages/
    ├── index.test.tsx
    └── ...
```

### Writing Component Tests

**Example: Testing a component**

```typescript
import { render, screen } from '@testing-library/react';
import { ErrorBoundary } from '@/components/ErrorBoundary';

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Test Content</div>
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders error UI when error occurs', () => {
    const ThrowError = () => {
      throw new Error('Test error');
    };
    
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );
    
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    
    consoleSpy.mockRestore();
  });
});
```

**Example: Testing API functions**

```typescript
import { apiClient } from '@/lib/api';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.post('http://localhost:8000/api/v1/auth/login', (req, res, ctx) => {
    return res(
      ctx.json({
        access_token: 'test-token',
        token_type: 'bearer',
        user: { id: 1, email: 'test@example.com' }
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('API Client', () => {
  it('handles successful login', async () => {
    const response = await apiClient.post('/auth/login', {
      email: 'test@example.com',
      password: 'password123'
    });
    
    expect(response.data.access_token).toBe('test-token');
  });
});
```

---

## Integration Testing

Integration tests verify that different parts of the application work together correctly.

### Database Integration Tests

```python
@pytest.mark.asyncio
async def test_user_authentication_flow(async_client: AsyncClient):
    """Test complete user authentication flow"""
    
    # 1. Signup
    signup_response = await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "full_name": "New User"
        }
    )
    assert signup_response.status_code == 201
    
    # 2. Login
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    me_response = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "newuser@example.com"
```

---

## E2E Testing

End-to-end tests simulate real user interactions.

### Playwright Setup (Planned)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Deal Management', () => {
  test('user can create a deal', async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000/auth/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Navigate to deals
    await page.goto('http://localhost:3000/deals');
    await expect(page).toHaveURL(/.*deals/);
    
    // Create new deal
    await page.click('button:has-text("New Deal")');
    await page.fill('input[name="customer_name"]', 'John Doe');
    await page.fill('input[name="customer_email"]', 'john@example.com');
    await page.fill('input[name="vehicle_make"]', 'Toyota');
    await page.fill('input[name="vehicle_model"]', 'Camry');
    await page.fill('input[name="vehicle_year"]', '2022');
    await page.fill('input[name="asking_price"]', '28000');
    await page.click('button:has-text("Create Deal")');
    
    // Verify deal created
    await expect(page.locator('text=John Doe')).toBeVisible();
  });
});
```

---

## Test Coverage

### Viewing Coverage Reports

**Backend:**
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Frontend:**
```bash
cd frontend
npm test -- --coverage
open coverage/lcov-report/index.html
```

### Coverage Goals

- **Overall**: 80% minimum
- **Critical paths**: 100%
  - Authentication
  - Deal creation/updates
  - Payment processing
- **Services**: 90%
- **Repositories**: 85%
- **API endpoints**: 95%

---

## Best Practices

### General

1. **Test Independence**: Each test should be independent and not rely on others
2. **Clear Names**: Use descriptive test names that explain what is being tested
3. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification
4. **Mock External Services**: Don't make real API calls in tests
5. **Test Edge Cases**: Include tests for error conditions and edge cases

### Backend

1. **Use Fixtures**: Leverage pytest fixtures for common setup
2. **Async Tests**: Mark async tests with `@pytest.mark.asyncio`
3. **Database Cleanup**: Always clean up test data after tests
4. **Environment Variables**: Use separate test configuration
5. **Fast Tests**: Keep unit tests fast by mocking external dependencies

### Frontend

1. **User Perspective**: Test from the user's perspective, not implementation details
2. **Accessibility**: Test for accessibility (ARIA labels, keyboard navigation)
3. **Error States**: Test loading and error states
4. **Mock API**: Use MSW or similar to mock API responses
5. **Snapshot Testing**: Use sparingly, only for stable UI components

---

## Continuous Integration

Tests are automatically run in CI/CD pipeline on:
- Push to main/develop branches
- Pull request creation/update

See `.github/workflows/ci-cd.yml` for configuration.

---

## Debugging Tests

### Backend

**Run with debugger:**
```bash
pytest --pdb
```

**Print output:**
```bash
pytest -s
```

**Verbose output:**
```bash
pytest -vv
```

### Frontend

**Debug in VS Code:**
Add to `.vscode/launch.json`:
```json
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/frontend/node_modules/.bin/jest",
  "args": ["--runInBand"],
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

---

## Test Data Management

### Factories and Builders

Create test data factories for consistent test objects:

```python
# tests/factories.py
from app.models import User, Deal

class UserFactory:
    @staticmethod
    def create(db, **kwargs):
        defaults = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed",
            "full_name": "Test User",
            "is_active": True
        }
        defaults.update(kwargs)
        user = User(**defaults)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
```

---

## Performance Testing

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class AutoDealGenieUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before running tasks"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
    
    @task
    def get_deals(self):
        self.client.get(
            "/api/v1/deals/",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(3)
    def get_deal_detail(self):
        self.client.get(
            "/api/v1/deals/1",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

Run with:
```bash
locust -f tests/load_test.py --host=http://localhost:8000
```

---

## Security Testing

### OWASP Testing

1. **SQL Injection**: Test with malicious inputs
2. **XSS**: Test script injection in inputs
3. **CSRF**: Verify CSRF protection
4. **Authentication**: Test token expiration and invalidation
5. **Authorization**: Test access control

### Example Security Tests

```python
@pytest.mark.asyncio
async def test_sql_injection_prevention(async_client: AsyncClient):
    """Test that SQL injection is prevented"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com' OR '1'='1",
            "password": "password"
        }
    )
    assert response.status_code in [400, 401]

@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    """Test that unauthorized users cannot access protected endpoints"""
    response = await async_client.get("/api/v1/deals/")
    assert response.status_code == 401
```

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Playwright](https://playwright.dev/)
- [MSW (Mock Service Worker)](https://mswjs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Troubleshooting

### Common Issues

**Issue: Tests fail with database connection error**
- Solution: Ensure test database is running and credentials are correct

**Issue: Async tests hang**
- Solution: Mark tests with `@pytest.mark.asyncio` and use async fixtures

**Issue: Frontend tests timeout**
- Solution: Increase timeout in jest.config.js or use `waitFor` from Testing Library

**Issue: Coverage not accurate**
- Solution: Check coverage exclusions in pyproject.toml and jest.config.js
