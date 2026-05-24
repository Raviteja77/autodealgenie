---
paths: "{backend/tests,frontend/__tests__,frontend/e2e}/**"
---

# Testing Rules (Auto-loaded for test files)

## Backend Tests (pytest)

```python
# tests/test_my_feature.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_deal_success(async_client: AsyncClient, auth_headers: dict):
    """Happy path: creating a deal returns 201 with the deal data."""
    response = await async_client.post(
        "/api/v1/deals/",
        json={"vehicle_make": "Toyota", "vehicle_model": "Camry", "vehicle_year": 2022, "asking_price": 28000},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["vehicle_make"] == "Toyota"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_deal_unauthenticated(async_client: AsyncClient):
    """Security: unauthenticated request must return 401."""
    response = await async_client.post("/api/v1/deals/", json={})
    assert response.status_code == 401
```

**Backend test rules:**
- Use SQLite in-memory for tests (configured in conftest.py)
- Mock external services: Redis, RabbitMQ, OpenAI, MarketCheck
- Test names describe behavior: `test_[action]_[condition]`
- One assert per test where possible
- Test both happy path AND the most likely failure mode

## Frontend Tests (Jest + Testing Library)

```tsx
// __tests__/VehicleCard.test.tsx
import { render, screen, fireEvent } from "@testing-library/react"
import { VehicleCard } from "@/components/organisms/VehicleCard"

describe("VehicleCard", () => {
  const mockVehicle = { id: "1", make: "Toyota", model: "Camry", year: 2022, price: 28000 }

  it("displays vehicle name and price", () => {
    render(<VehicleCard vehicle={mockVehicle} onFavorite={jest.fn()} />)
    expect(screen.getByText("2022 Toyota Camry")).toBeInTheDocument()
    expect(screen.getByText("$28,000")).toBeInTheDocument()
  })

  it("calls onFavorite when heart button is clicked", () => {
    const onFavorite = jest.fn()
    render(<VehicleCard vehicle={mockVehicle} onFavorite={onFavorite} />)
    fireEvent.click(screen.getByTestId("favorite-button"))
    expect(onFavorite).toHaveBeenCalledWith("1")
  })
})
```

## E2E Tests (Playwright)

```ts
// e2e/search-flow.spec.ts
import { test, expect } from "@playwright/test"

test("user can search for vehicles and save a favorite", async ({ page }) => {
  await page.goto("/auth/login")
  await page.fill('[data-testid="email-input"]', "test@example.com")
  await page.fill('[data-testid="password-input"]', "password123")
  await page.click('[data-testid="login-button"]')

  await expect(page).toHaveURL("/dashboard/search")
  await page.fill('[data-testid="make-input"]', "Toyota")
  await page.click('[data-testid="search-button"]')

  await expect(page.getByTestId("vehicle-card")).toBeVisible()
  await page.click('[data-testid="favorite-button"]')
  await expect(page.getByText("Saved to favorites")).toBeVisible()
})
```

**E2E test rules:**
- Always use `data-testid` selectors — CSS classes change, these don't
- Each test sets up its own state — no shared state between tests
- Run against a real test database, not mocks
- Test critical user journeys end-to-end (not just component behavior)
